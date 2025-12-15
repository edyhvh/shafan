"""Main Hebrew text extractor class and processing logic."""

import cv2
import logging
import numpy as np
from pathlib import Path
from tqdm import tqdm
from typing import Tuple, Optional

from .detection import (
    find_main_box_from_contours,
    find_main_box_with_hough,
    find_main_box_from_projection,
)
from .utils import (
    get_fallback_coords,
    VERTICAL_WIDTH_RANGE,
    TITLE_SCAN_HEIGHT,
    TITLE_MIN_HEIGHT,
    TITLE_MAX_HEIGHT,
    split_wide_region,
    validate_column_width,
    reject_first_column,
)
from .validation import (
    fix_wrong_column_detection,
    fix_right_edge_expansion,
    fix_corinthians2_000068,
)
from .logger import ImageLogger, log_summary

logger = logging.getLogger(__name__)


class HebrewTextExtractor:
    """Class to handle dynamic Hebrew text extraction from images."""

    def __init__(self, input_dir: Path, output_dir: Path):
        """
        Initialize the extractor.

        Args:
            input_dir: Directory containing input images
            output_dir: Directory to save cropped images
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        # Special handling for john1: skip 000006.png and 000008.png,
        # and from 000009.png onwards, process only odd-numbered images
        self.is_john1 = "john1" in str(input_dir).lower()

    def _preprocess(self, image: cv2.Mat) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert image to grayscale and adaptive-thresholded binary mask.

        Args:
            image: Source BGR image.

        Returns:
            Tuple of (gray image, thresholded image).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            12,
        )
        return gray, thresh

    def _is_box_reasonable(
        self, box: Tuple[int, int, int, int], image_shape: Tuple[int, int, int]
    ) -> bool:
        """
        Validate whether a detected box matches expected geometry.

        Args:
            box: Bounding box tuple (x, y, w, h).
            image_shape: Shape of the original image.

        Returns:
            True if the box fits expected constraints, False otherwise.
        """
        x, y, w, h = box
        img_h, img_w = image_shape[:2]

        max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(img_w * 0.6))
        min_allowed_width = max(600, VERTICAL_WIDTH_RANGE[0] - 200)
        width_ok = min_allowed_width <= w <= max_allowed_width

        min_height_required = max(int(img_h * 0.4), 1500)
        height_ok = h >= min_height_required

        within_bounds = (
            x >= 0 and y >= 0 and x + w <= img_w and y + h <= img_h
        )

        center_x = x + w / 2
        max_x_percent = int(img_w * 0.35)
        max_x_absolute = 600
        max_x = max(max_x_percent, max_x_absolute)
        position_ok = (
            center_x <= img_w * 0.50
            and x <= max_x
            and x >= 50
        )

        return width_ok and height_ok and within_bounds and position_ok

    def _detect_title_region(
        self, thresh: np.ndarray, box: Tuple[int, int, int, int]
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the horizontal title region near the top of the main column.

        Args:
            thresh: Thresholded binary image.
            box: Bounding box (x, y, w, h) of the main column.

        Returns:
            Bounding box of the detected title or None.
        """
        x, y, w, h = box
        if h <= 0 or w <= 0:
            return None

        scan_height = min(TITLE_SCAN_HEIGHT, h)
        roi = thresh[y : y + scan_height, x : x + w]
        if roi.size == 0:
            return None

        # Emphasize horizontal structures
        horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
        closed = cv2.morphologyEx(roi, cv2.MORPH_CLOSE, horiz_kernel, iterations=2)

        contours, _ = cv2.findContours(
            closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        candidates: list = []
        for cnt in contours:
            tx, ty, tw, th = cv2.boundingRect(cnt)
            width_ok = tw >= int(0.5 * w)
            height_ok = TITLE_MIN_HEIGHT <= th <= TITLE_MAX_HEIGHT
            top_ok = ty <= scan_height
            if width_ok and height_ok and top_ok:
                candidates.append((tx, ty, tw, th))

        if not candidates:
            return None

        title_box = min(candidates, key=lambda b: b[1])  # top-most
        abs_box = (x + title_box[0], y + title_box[1], title_box[2], title_box[3])
        logger.info(
            "Detected title region: x=%d, y=%d, w=%d, h=%d",
            abs_box[0],
            abs_box[1],
            abs_box[2],
            abs_box[3],
        )
        return abs_box

    def detect_hebrew_column(self, image: cv2.Mat, img_logger: Optional[ImageLogger] = None) -> Tuple[Tuple[int, int, int, int], str]:
        """
        Dynamically detect the Hebrew text column using contours and line detection.

        Args:
            image: OpenCV image matrix
            img_logger: Optional ImageLogger for organized logging

        Returns:
            Tuple of ((x, y, w, h), method_used) where method_used is the detection method name
        """
        height, width = image.shape[:2]
        if height == 0 or width == 0:
            fallback = get_fallback_coords(width, height)
            return (
                (
                    fallback["x"],
                    fallback["y"],
                    fallback["w"],
                    fallback["h"],
                ),
                "fallback",
            )

        gray, thresh = self._preprocess(image)

        # Try detection methods in order
        box = find_main_box_from_contours(thresh)
        method_used = "contour"
        if box is None:
            logger.debug("Contour detection failed; trying Hough lines.")
            box = find_main_box_with_hough(gray, thresh)
            if box is not None:
                method_used = "hough"
        if box is None:
            logger.debug("Hough detection failed; trying projection-based search.")
            box = find_main_box_from_projection(thresh)
            if box is not None:
                method_used = "projection"

        if box is None:
            logger.debug("All detection methods failed; using fallback coordinates.")
            fallback = get_fallback_coords(width, height)
            return (
                (
                    fallback["x"],
                    fallback["y"],
                    fallback["w"],
                    fallback["h"],
                ),
                "fallback",
            )

        # Validate and refine if needed
        if not self._is_box_reasonable(box, image.shape):
            logger.debug("Detected box out of expected range; refining with projection.")
            refined_box = find_main_box_from_projection(thresh)
            if refined_box is not None and self._is_box_reasonable(
                refined_box, image.shape
            ):
                box = refined_box
                method_used = "projection"

        # Additional validation: ensure x is reasonable
        x, y, w, h = box
        max_x_percent = int(width * 0.35)
        max_x_absolute = 600
        max_x = max(max_x_percent, max_x_absolute)
        if x > max_x:
            logger.debug("Box starts too far right (x=%d), trying projection.", x)
            refined_box = find_main_box_from_projection(thresh)
            if refined_box is not None and self._is_box_reasonable(
                refined_box, image.shape
            ):
                box = refined_box
                method_used = "projection"
            else:
                if img_logger:
                    img_logger.log_warning("All detection methods failed validation")
                fallback = get_fallback_coords(width, height)
                return (
                    (
                        fallback["x"],
                        fallback["y"],
                        fallback["w"],
                        fallback["h"],
                    ),
                    "fallback",
                )

        if not self._is_box_reasonable(box, image.shape):
            if img_logger:
                img_logger.log_warning("Detected box failed validation")
            fallback = get_fallback_coords(width, height)
            return (
                (
                    fallback["x"],
                    fallback["y"],
                    fallback["w"],
                    fallback["h"],
                ),
                "fallback",
            )

        # Detect and include title region
        title_box = self._detect_title_region(thresh, box)
        if title_box:
            tx, ty, tw, th = title_box
            x, y, w, h = box
            new_x = min(x, tx)
            # CRITICAL: Always keep y=0 to preserve enumeration/title at top
            new_y = 0
            new_w = max(x + w, tx + tw) - new_x
            new_h = max(y + h, ty + th) - new_y
            box = (new_x, new_y, new_w, new_h)
        else:
            # CRITICAL: Ensure y=0 even if no title detected
            x, y, w, h = box
            box = (x, 0, w, h)

        # Final check: split if too wide or starts too close to left
        x, y, w, h = box
        if w > 900 or (w > 800 and x < 150):
            logger.debug(
                "Final box is too wide (w=%d, x=%d), splitting to get second column.",
                w,
                x,
            )
            if x < 150:
                new_x = max(400, int(width * 0.25))
            else:
                new_x = max(x + 400, int(x + w * 0.3))
            x = new_x
            w = min(1100, width - x)
            box = (x, y, w, h)
            if img_logger:
                img_logger.log_info(f"Split wide region: x={x}, w={w}")

        # Apply general fixes for common problems
        # Fix 1: Wrong column detection (column too far right)
        box = fix_wrong_column_detection(thresh, box, width)
        
        # Fix 2: Right edge expansion (text too close to edge)
        box = fix_right_edge_expansion(thresh, box, width)

        logger.debug(
            "Final bounding box: x=%d, y=%d, w=%d, h=%d", box[0], box[1], box[2], box[3]
        )
        return box, method_used

    def _is_image_blank(self, image: np.ndarray) -> bool:
        """
        Check if an image is blank or has very little content.

        Args:
            image: BGR image

        Returns:
            True if image appears to be blank
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        std = np.std(gray)
        return std < 15

    def _should_process_image(self, image_number: int, img_logger: Optional[ImageLogger] = None) -> Tuple[bool, Optional[str]]:
        """
        Determine if an image should be processed based on special rules.

        Args:
            image_number: Image number from filename
            img_logger: Optional ImageLogger for organized logging

        Returns:
            Tuple of (should_process, skip_reason)
        """
        # Special handling for john1
        if self.is_john1:
            # Skip specific images
            if image_number in [6, 8]:
                reason = "not part of manuscript for john1"
                if img_logger:
                    img_logger.log_info(f"Skipped: {reason}")
                return False, reason
            # From 000009.png onwards, process only odd-numbered images
            if image_number >= 9:
                if image_number % 2 == 0:
                    reason = "john1: only odd from 000009 onwards"
                    if img_logger:
                        img_logger.log_info(f"Skipped: {reason}")
                    return False, reason
            # For images before 000009, process only even-numbered
            elif image_number % 2 == 1:
                reason = "typically no Hebrew text"
                if img_logger:
                    img_logger.log_info(f"Skipped: {reason}")
                return False, reason
        else:
            # Normal behavior: skip odd-numbered images
            if image_number % 2 == 1:
                reason = "typically no Hebrew text"
                if img_logger:
                    img_logger.log_info(f"Skipped: {reason}")
                return False, reason

        return True, None

    def process_single_image(self, image_path: Path, use_logger: bool = True) -> bool:
        """
        Process a single image: load, detect, crop, and save.

        Args:
            image_path: Path to the input image
            use_logger: Whether to use ImageLogger for organized output

        Returns:
            True if successful, False otherwise
        """
        image_logger = None
        if use_logger:
            image_logger = ImageLogger(image_path.name, logger)
            image_logger.__enter__()

        try:
            image_number = int(image_path.stem)

            # Check if image should be processed
            should_process, skip_reason = self._should_process_image(image_number, image_logger)
            if not should_process:
                if image_logger:
                    image_logger.__exit__(None, None, None)
                return False

            # Read the image
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                if image_logger:
                    image_logger.log_warning("Failed to load image")
                    image_logger.__exit__(None, None, None)
                return False

            # Check if image is blank
            if self._is_image_blank(image):
                if image_logger:
                    image_logger.log_info("Skipped: blank image")
                    image_logger.__exit__(None, None, None)
                return False

            height, width = image.shape[:2]

            # Detect bounding box
            (x, y, w, h), method_used = self.detect_hebrew_column(image, image_logger)

            # Apply specific fix for corinthians2/000068.png
            is_corinthians2 = "corinthians2" in str(self.input_dir).lower()
            if is_corinthians2 and image_path.name == "000068.png":
                (x, y, w, h) = fix_corinthians2_000068((x, y, w, h), width)

            # Validate and clamp coordinates
            x = min(max(0, x), max(0, width - 1))
            # CRITICAL: Always start from top (y=0) to preserve enumeration
            y = 0
            w = max(1, min(w, width - x))
            
            # Final split check if box is still too wide (original logic)
            if w > 900 or (w > 800 and x < 150):
                logger.debug(
                    "Final box is too wide (w=%d, x=%d), splitting.",
                    w,
                    x,
                )
                if x < 150:
                    new_x = max(400, int(width * 0.25))
                else:
                    new_x = max(x + 400, int(x + w * 0.3))
                x = new_x
                w = min(1100, width - x)
                if image_logger:
                    image_logger.log_info(f"Split wide region: x={x}, w={w}")

            # Ensure height covers most of the page (85-95%)
            min_height = int(height * 0.85)
            h = max(min_height, min(h, height - y))

            # Apply padding to avoid cutting text at edges
            # Based on analysis: text boundaries are often 0-1px from detected box edges
            PADDING_LEFT = 40
            PADDING_RIGHT = 40
            PADDING_BOTTOM = 100
            PADDING_TOP = 0  # Keep y=0 to preserve enumeration at top

            new_x = max(0, x - PADDING_LEFT)
            new_y = max(0, y - PADDING_TOP)
            new_w = min(width - new_x, w + PADDING_LEFT + PADDING_RIGHT)
            new_h = min(height - new_y, h + PADDING_TOP + PADDING_BOTTOM)

            x, y, w, h = new_x, new_y, new_w, new_h

            # Crop
            cropped = image[y : y + h, x : x + w]

            # Create output path
            output_filename = image_path.name
            output_path = self.output_dir / output_filename
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Save
            success = cv2.imwrite(str(output_path), cropped)
            if not success:
                logger.error(f"Failed to save cropped image: {output_path}")
                if image_logger:
                    image_logger.log_warning("Failed to save cropped image")
                    image_logger.__exit__(None, None, None)
                return False

            if image_logger:
                image_logger.set_success(box=(x, y, w, h), method=method_used)
                image_logger.__exit__(None, None, None)
            else:
                logger.info(
                    f"Saved cropped image to {output_path} (Box: {x},{y},{w},{h})"
                )
            return True

        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
            if image_logger:
                image_logger.log_warning(f"Error: {e}")
                image_logger.__exit__(None, None, None)
            return False

    def process_all_images(self) -> Tuple[int, int]:
        """
        Process all images in the input directory.

        Returns:
            Tuple of (successful_count, total_count)
        """
        if not self.input_dir.exists():
            logger.error(f"Input directory not found: {self.input_dir}")
            return 0, 0

        image_files = []
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.tiff", "*.bmp"]:
            image_files.extend(self.input_dir.glob(ext))
        # Case insensitive search
        for ext in ["*.PNG", "*.JPG", "*.JPEG"]:
            image_files.extend(self.input_dir.glob(ext))

        image_files = sorted(list(set(image_files)))  # Remove duplicates and sort

        if not image_files:
            logger.warning(f"No image files found in {self.input_dir}")
            return 0, 0

        logger.info(f"Found {len(image_files)} images to process in {self.input_dir}")

        successful = 0
        skipped = 0
        with tqdm(total=len(image_files), desc="Processing images", ncols=80) as pbar:
            for image_path in image_files:
                result = self.process_single_image(image_path, use_logger=True)
                if result:
                    successful += 1
                else:
                    # Check if it was skipped (not an error)
                    try:
                        image_number = int(image_path.stem)
                        should_process, _ = self._should_process_image(image_number)
                        if not should_process:
                            skipped += 1
                        elif self._is_image_blank(cv2.imread(str(image_path))):
                            skipped += 1
                    except:
                        pass
                pbar.update(1)

        log_summary(logger, successful, len(image_files), skipped)
        return successful, len(image_files)
