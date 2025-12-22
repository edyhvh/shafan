#!/usr/bin/env python3
"""
Script to extract Hebrew text columns from biblical manuscript images using dynamic OpenCV detection.

This script processes images, detects the central Hebrew text column (including title),
and crops them dynamically. It handles variations in page layout and falls back to
approximate coordinates if detection fails.

Usage:
    python scripts/get_images_hebrew_text.py --input-dir data/images/philemon --output-dir data/temp/philemon
"""

import cv2
import logging
import argparse
import numpy as np
from pathlib import Path
from tqdm import tqdm
from typing import Tuple, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fallback coordinates - use similar to successful detection (x=493, w=703 from 000004.png)
# But adjust based on typical page width (around 1700px)
# Second column typically starts around 400-500px and has width 700-1100px
def get_fallback_coords(width: int, height: int) -> dict:
    """Get fallback coordinates based on image dimensions."""
    # Estimate second column position: typically 25-30% from left
    x = int(width * 0.28)  # ~28% from left (similar to x=493 for 1700px width)
    # Width: typically 700-1100px, use ~40% of page width or 700px minimum
    w = max(700, min(1100, int(width * 0.4)))
    return {
        "x": x,
        "y": 0,  # CRITICAL: Start from top to preserve enumeration
        "w": w,
        "h": height,  # Full height
    }

FALLBACK_COORDS = {
    "x": 150,
    "y": 0,
    "w": 1030,
    "h": 3070,
}

# Expected geometry for the central Hebrew column
VERTICAL_WIDTH_RANGE = (800, 1200)
VERTICAL_MIN_HEIGHT = 2000
VERTICAL_X_RANGE = (100, 300)
TITLE_SCAN_HEIGHT = 400
TITLE_MIN_HEIGHT = 25
TITLE_MAX_HEIGHT = 220

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

    def _find_main_box_from_contours(
        self, thresh: np.ndarray, margin: int = 20
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Find the main vertical column using contour analysis.

        Args:
            thresh: Binary image after thresholding.
            margin: Pixels to skip from borders to avoid noise.

        Returns:
            Bounding box (x, y, w, h) or None if not found.
        """
        height, width = thresh.shape[:2]
        if width <= 2 * margin or height <= 2 * margin:
            return None

        roi = thresh[margin : height - margin, margin : width - margin]

        # Use more conservative morphological operations to avoid merging adjacent columns
        # Horizontal kernel to connect characters in words/lines (smaller to avoid merging columns)
        h_kernel_size = max(3, int(width * 0.015))  # Reduced from 0.02
        v_kernel_size = max(8, int(height * 0.008))  # Reduced from 0.01
        kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_size, 3))
        kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (3, v_kernel_size))
        
        # First dilate horizontally to connect text in lines (fewer iterations)
        dilated_h = cv2.dilate(roi, kernel_horizontal, iterations=2)  # Reduced from 3
        # Then dilate vertically to connect lines into columns (fewer iterations)
        dilated = cv2.dilate(dilated_h, kernel_vertical, iterations=3)  # Reduced from 4
        
        # Smaller closing kernel to avoid merging columns
        closing_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # Reduced from 5x5
        dilated = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, closing_kernel, iterations=1)  # Reduced from 2

        contours, _ = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        candidate_boxes: List[Tuple[Tuple[int, int, int, int], float]] = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            x += margin
            y += margin

            # STRICTER width validation: minimum 800px, maximum 1400px or 60% of page width
            max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(width * 0.6))
            width_ok = VERTICAL_WIDTH_RANGE[0] <= w <= max_allowed_width  # Minimum 800px, not 500px
            # Height should be substantial portion of image
            height_ok = h >= max(VERTICAL_MIN_HEIGHT - 200, int(0.4 * height))
            # CRITICAL: Find ALL valid columns starting from x=0 to find first AND second column
            # Don't filter by x position here - we need to find ALL columns to select the second one
            center_x = x + w / 2
            x_ok = (x >= 0 and x <= width * 0.8 and  # Allow wide range to find ALL columns including first
                   center_x <= width * 0.8)  # Center can be anywhere in left 80% to find all columns
            # Aspect ratio should be tall (vertical column)
            aspect_ok = h / max(1, w) > 1.5

            if width_ok and height_ok and x_ok and aspect_ok:
                # Score by area and centrality (prefer left-center position)
                area = w * h
                # Prefer columns closer to ideal position (30% from left)
                ideal_x = width * 0.3
                centrality_score = 1.0 / (1.0 + abs(center_x - ideal_x) / (width * 0.2))
                # Prefer widths closer to expected range (1000-1100px)
                ideal_width = (VERTICAL_WIDTH_RANGE[0] + VERTICAL_WIDTH_RANGE[1]) / 2
                width_score = 1.0 / (1.0 + abs(w - ideal_width) / 200)
                score = area * centrality_score * width_score
                candidate_boxes.append(((x, y, w, h), score))

        if not candidate_boxes:
            return None

        # Sort by x position (left to right) to find columns in order
        candidate_boxes.sort(key=lambda b: b[0][0])  # Sort by x position
        
        # CRITICAL: Must find at least 2 columns to select the second one
        # If only 1 column found, it's likely the first column and we should reject it
        if len(candidate_boxes) < 2:
            logger.info("Contour detection: found only %d column(s), need at least 2 to select second. Rejecting.", len(candidate_boxes))
            return None
        
        # Select the second column from left (index 1)
        selected_box = candidate_boxes[1][0]  # Second column from left
        logger.info("Contour detection: found %d columns, selecting second from left (x=%d)", 
                   len(candidate_boxes), selected_box[0])
        
        # Final validation: ensure minimum width of 800px and reject first column (x too close to 0)
        x, y, w, h = selected_box
        if w < VERTICAL_WIDTH_RANGE[0]:
            logger.info("Contour detection found box too narrow (w=%d), rejecting.", w)
            return None
        # CRITICAL: Reject columns starting at x=0 or too close to left edge (likely first column)
        if x < 50:
            logger.info("Contour detection found column starting too close to left edge (x=%d, likely first column), rejecting.", x)
            return None
        
        # CRITICAL: Expand vertical range to preserve enumeration at top
        # ALWAYS start from very top (y=0 or small margin <50px) to preserve enumeration/verse numbers
        # Ignore the detected y position - we need the full column from top
        y0_start = max(0, min(50, int(height * 0.02)))  # Start from top, max 50px margin (2% of height)
        # Extend to near bottom (90-95% of page to ensure we capture all text)
        y1_end = min(height - 1, int(height * 0.93))  # Extend to 93% of page
        h_expanded = y1_end - y0_start
        
        # Ensure we capture enough height (at least 85% of page for full text)
        min_height = int(height * 0.85)
        if h_expanded < min_height:
            # Expand downward if possible
            y1_end = min(height - 1, y0_start + min_height)
            h_expanded = y1_end - y0_start
        
        # Update box with expanded vertical range
        selected_box = (x, y0_start, w, h_expanded)
        
        logger.info(
            "Contour-based column: x=%d, y=%d, w=%d, h=%d",
            selected_box[0],
            selected_box[1],
            selected_box[2],
            selected_box[3],
        )
        return selected_box

    def _find_main_box_with_hough(
        self, gray: np.ndarray, thresh: np.ndarray
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Fallback detection using Hough lines to locate vertical borders.

        Args:
            gray: Grayscale image.
            thresh: Thresholded image.

        Returns:
            Bounding box (x, y, w, h) or None.
        """
        height, width = gray.shape[:2]
        
        # Use adaptive thresholding result for better edge detection
        edges = cv2.Canny(thresh, 50, 150, apertureSize=3)

        # Detect vertical lines (for column borders)
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=max(height // 4, 500),
            maxLineGap=50,
        )

        if lines is None:
            return None

        vertical_xs: List[int] = []
        horizontal_ys: List[int] = []
        
        for line in lines[:, 0, :]:
            x1, y1, x2, y2 = line
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            
            # More strict vertical line detection
            if dx < 15 and dy > 300:  # Vertical lines
                # CRITICAL: Find ALL vertical lines to detect all columns (including first and second)
                avg_x = (x1 + x2) / 2
                # Allow wider range to find all columns from left edge
                if 0 <= avg_x <= width * 0.8:  # Find lines in left 80% of page
                    vertical_xs.extend([x1, x2])
            
            # Horizontal lines for title detection
            if dy < 15 and dx > 300:  # Horizontal lines
                if 0 <= min(y1, y2) <= TITLE_SCAN_HEIGHT + 300:
                    horizontal_ys.extend([y1, y2])

        if len(vertical_xs) < 2:
            return None

        # CRITICAL: Find ALL vertical lines to detect all columns (including first and second)
        # Don't filter too strictly - we need to find all columns to select the second one
        filtered_xs = [x for x in vertical_xs if 0 <= x <= width * 0.8]  # Allow wider range to find all columns
        
        if len(filtered_xs) < 2:
            return None
        
        # Group nearby x positions into clusters
        # Use smaller threshold to create more clusters (find more column boundaries)
        filtered_xs_sorted = sorted(filtered_xs)
        clusters: List[List[int]] = []
        if len(filtered_xs_sorted) == 0:
            return None
        current_cluster = [filtered_xs_sorted[0]]
        
        for x in filtered_xs_sorted[1:]:
            # Reduced threshold from 80px to 50px to create more distinct clusters
            if x - current_cluster[-1] < 50:  # Group lines within 50px (tighter clustering)
                current_cluster.append(x)
            else:
                clusters.append(current_cluster)
                current_cluster = [x]
        clusters.append(current_cluster)
        
        # If we have very few clusters, try even tighter clustering
        if len(clusters) < 3 and len(filtered_xs_sorted) > 2:
            # Retry with even tighter clustering (30px)
            clusters = []
            current_cluster = [filtered_xs_sorted[0]]
            for x in filtered_xs_sorted[1:]:
                if x - current_cluster[-1] < 30:
                    current_cluster.append(x)
                else:
                    clusters.append(current_cluster)
                    current_cluster = [x]
            clusters.append(current_cluster)
        
        # Find all valid column pairs and select the second one from left
        # CRITICAL: Only consider adjacent cluster pairs (i, i+1) to avoid creating invalid wide columns
        valid_columns: List[Tuple[int, int, float]] = []  # (left_x, right_x, score)
        
        for i in range(len(clusters) - 1):
            # Only consider adjacent clusters (i and i+1) to form valid column boundaries
            j = i + 1
            left_x = min(clusters[i])
            right_x = max(clusters[j])
            w = right_x - left_x
            
            # Check if width is reasonable for Hebrew column
            if VERTICAL_WIDTH_RANGE[0] - 300 <= w <= VERTICAL_WIDTH_RANGE[1] + 400:
                # Score by centrality and width appropriateness
                center_x = (left_x + right_x) / 2
                ideal_x = width * 0.3
                centrality = 1.0 / (1.0 + abs(center_x - ideal_x) / (width * 0.2))
                
                # Width score - prefer widths in the expected range
                if VERTICAL_WIDTH_RANGE[0] <= w <= VERTICAL_WIDTH_RANGE[1]:
                    width_score = 1.0
                elif VERTICAL_WIDTH_RANGE[0] - 200 <= w < VERTICAL_WIDTH_RANGE[0]:
                    width_score = 0.8
                elif VERTICAL_WIDTH_RANGE[1] < w <= VERTICAL_WIDTH_RANGE[1] + 300:
                    width_score = 0.8
                else:
                    width_score = 0.5
                
                # CRITICAL: Reject columns that start too close to left edge (x < 50) - these are likely first column
                # But allow them if we have very few columns (fallback case)
                position_penalty = 1.0
                if left_x < 50 and len(clusters) > 3:
                    position_penalty = 0.3  # Heavily penalize first column
                
                score = centrality * width_score * position_penalty
                valid_columns.append((left_x, right_x, score))
        
        if not valid_columns:
            # Fallback: use min/max of filtered lines
            left_x = min(filtered_xs)
            right_x = max(filtered_xs)
        else:
            # Sort by left_x position (left to right) and select second column
            valid_columns.sort(key=lambda c: c[0])  # Sort by left_x
            # CRITICAL: Must find at least 2 columns to select the second one
            if len(valid_columns) < 2:
                logger.info("Hough detection: found only %d column(s), need at least 2 to select second. Rejecting.", len(valid_columns))
                return None
            left_x, right_x, _ = valid_columns[1]  # Second column from left
            logger.info("Hough detection: found %d columns, selecting second from left (x=%d)", 
                       len(valid_columns), left_x)
            
            # CRITICAL: Validate that the selected column doesn't start too close to left edge
            # If it starts before 250px, it likely includes the first column
            # In this case, try to find a better column or adjust the position
            min_x_threshold = max(250, int(width * 0.15))  # At least 250px or 15% of page width
            if left_x < min_x_threshold:
                logger.info("Hough detection: selected column starts too close to left (x=%d, min=%d), checking for better option.", 
                           left_x, min_x_threshold)
                # Look for columns that start after threshold but are still reasonable
                better_columns = [col for col in valid_columns if col[0] >= min_x_threshold]
                if better_columns:
                    # Use the leftmost column that starts after threshold (this should be the second column)
                    better_columns.sort(key=lambda c: c[0])
                    left_x, right_x, _ = better_columns[0]
                    logger.info("Hough detection: using better column that starts after threshold (x=%d)", left_x)
                else:
                    # If no better option, adjust the current column to start at a safer position
                    # Second column typically starts around 400-500px from left
                    adjusted_x = max(400, int(width * 0.25))
                    # Adjust width to maintain reasonable size, but ensure we don't cut text
                    w_current = right_x - left_x
                    # Ensure minimum width of 800px to avoid cutting text
                    w_adjusted = max(800, min(w_current, 1100))
                    right_x = adjusted_x + w_adjusted
                    left_x = adjusted_x
                    logger.info("Hough detection: adjusted column position to avoid first column (x=%d, w=%d)", left_x, w_adjusted)

        # Ensure reasonable width - expand if too narrow, but allow some flexibility
        w_detected = right_x - left_x
        if w_detected < VERTICAL_WIDTH_RANGE[0] - 200:
            # Try to expand to minimum width if possible
            if left_x + VERTICAL_WIDTH_RANGE[0] <= width * 0.7:
                right_x = left_x + VERTICAL_WIDTH_RANGE[0]
            else:
                # If can't expand, allow narrower columns (minimum 600px)
                if w_detected < 600:
                    logger.info("Hough detection: column too narrow (w=%d), rejecting.", w_detected)
                    return None
        if right_x - left_x > VERTICAL_WIDTH_RANGE[1] + 300:
            right_x = left_x + VERTICAL_WIDTH_RANGE[1] + 150

        # Find vertical extent
        y_min, y_max = 0, height - 1
        if horizontal_ys:
            y_min = max(0, min(horizontal_ys) - 20)

        # Refine vertical range using non-zero pixels inside tentative box
        mask = thresh[:, max(0, left_x - 10) : min(width, right_x + 10)]
        nz = cv2.findNonZero(mask)
        if nz is not None and len(nz) > 0:
            y_coords = nz[:, 0, 1]
            y_min_refined = max(0, int(np.min(y_coords) - 15))
            y_max_refined = min(height - 1, int(np.max(y_coords) + 15))
            y_min = min(y_min, y_min_refined)
            y_max = max(y_max, y_max_refined)

        if y_max - y_min < VERTICAL_MIN_HEIGHT - 200:
            y_max = min(height - 1, y_min + VERTICAL_MIN_HEIGHT)

        # Calculate width before creating box
        w_calculated = right_x - left_x
        
        # CRITICAL: Ensure width is sufficient to avoid cutting text on the right
        # If width is less than 800px and we're not at the edge, try to expand
        if w_calculated < 800 and right_x < width * 0.9:
            # Try to expand width to at least 800px if possible
            max_expand_x = min(width * 0.9, left_x + 1100)  # Don't go beyond 90% of page width
            w_expanded = max_expand_x - left_x
            if w_expanded >= 800:
                w_calculated = min(1100, w_expanded)
                right_x = left_x + w_calculated
                logger.info("Hough detection: expanded width from %d to %d to avoid cutting text", 
                           right_x - left_x - (w_calculated - (right_x - left_x - w_calculated)), w_calculated)
        
        box = (
            max(0, left_x),
            max(0, y_min),
            min(width - max(0, left_x), right_x - left_x),
            max(0, y_max - y_min),
        )
        
        # Validate the detected box - reject if clearly wrong
        x, y, w, h = box
        center_x = x + w / 2
        
        # The Hebrew column should be in the left-center region
        # Center should be before 50% of page width
        if center_x > width * 0.5:
            logger.info("Hough detection found column too far right (center_x=%.1f), rejecting.", center_x)
            return None
        
        # CRITICAL: Hebrew column is second from left, so it should NOT start at x=0 (that's first column)
        # According to prompt: second column typically starts at 200-600px from left edge
        # For john1, we've seen that columns starting before 250px include the first rectangle
        # So we need stricter validation: minimum x should be 250px (or 15% of page width)
        min_x_threshold = max(250, int(width * 0.15))  # At least 250px or 15% of page width
        max_x_percent = int(width * 0.35)  # 35% of page width
        max_x_absolute = 600  # Absolute max 600px as per prompt
        max_x = max(max_x_percent, max_x_absolute)  # Use more permissive limit
        
        if x < min_x_threshold:
            logger.info("Hough detection found column starting too close to left edge (x=%d, min=%d, likely includes first column), rejecting.", 
                       x, min_x_threshold)
            return None
        if x > max_x:
            logger.info("Hough detection found column at invalid x position (x=%d, should be <=%d), rejecting.", 
                       x, max_x)
            return None
        
        # Width validation: allow some flexibility for detected columns
        # Minimum can be 600px (if detected), ideal is 800-1200px, max is 1400px or 60% of page
        max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(width * 0.6))
        min_allowed_width = max(600, VERTICAL_WIDTH_RANGE[0] - 200)  # Allow narrower if detected
        if w < min_allowed_width or w > max_allowed_width:
            logger.info("Hough detection found unreasonable width (w=%d, min=%d, max=%d), rejecting.", 
                       w, min_allowed_width, max_allowed_width)
            return None
        
        # CRITICAL: Expand vertical range to preserve enumeration at top
        # ALWAYS start from very top (y=0 or small margin <50px) to preserve enumeration/verse numbers
        # Ignore the detected y position - we need the full column from top
        y0_start = max(0, min(50, int(height * 0.02)))  # Start from top, max 50px margin (2% of height)
        # Extend to near bottom (90-95% of page to ensure we capture all text)
        y1_end = min(height - 1, int(height * 0.93))  # Extend to 93% of page
        h_expanded = y1_end - y0_start
        
        # Ensure we capture enough height (at least 85% of page for full text)
        min_height = int(height * 0.85)
        if h_expanded < min_height:
            # Expand downward if possible
            y1_end = min(height - 1, y0_start + min_height)
            h_expanded = y1_end - y0_start
        
        # CRITICAL: Ensure width is sufficient to avoid cutting text on the right
        # If width is less than 800px and we're not at the edge, try to expand
        if w < 800 and x + w < width * 0.9:
            # Try to expand width to at least 800px if possible
            max_expand_x = min(width * 0.9, x + 1100)  # Don't go beyond 90% of page width
            w_expanded = min(1100, max_expand_x - x)
            if w_expanded >= 800:
                w = w_expanded
                logger.info("Hough detection: expanded width from %d to %d to avoid cutting text", w_expanded - (w_expanded - w), w)
        
        # Update box with expanded vertical range
        box = (x, y0_start, w, h_expanded)
        
        logger.info(
            "Hough-based column: x=%d, y=%d, w=%d, h=%d", box[0], box[1], box[2], box[3]
        )
        return box

    def _find_main_box_from_projection(
        self, thresh: np.ndarray
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Fallback using horizontal/vertical projections to locate dense text bands.

        Args:
            thresh: Thresholded binary image.

        Returns:
            Bounding box (x, y, w, h) or None.
        """
        height, width = thresh.shape[:2]
        if height == 0 or width == 0:
            return None

        sum_x = thresh.sum(axis=0)
        sum_y = thresh.sum(axis=1)

        def longest_run(array: np.ndarray, ratio: float = 0.02) -> Optional[Tuple[int, int, int]]:
            if array.size == 0:
                return None
            max_val = array.max()
            if max_val == 0:
                return None
            threshold = max(1, ratio * float(max_val))
            indices = np.where(array > threshold)[0]
            if indices.size == 0:
                return None
            splits = np.where(np.diff(indices) > 1)[0]
            starts = [indices[0]]
            ends: List[int] = []
            for idx in splits:
                ends.append(indices[idx])
                starts.append(indices[idx + 1])
            ends.append(indices[-1])
            spans = [(s, e, e - s) for s, e in zip(starts, ends)]
            return max(spans, key=lambda t: t[2])

        # Find all dense text regions (columns) across the page
        # CRITICAL: We need to find multiple columns and select the second one from left
        all_columns: List[Tuple[int, int, int, float]] = []  # (x0, x1, w, score)
        
        # Search in wider range (left 80% of page) to find ALL columns including first
        search_end = int(width * 0.8)
        search_sum_x = sum_x[:search_end]
        
        # Try many different thresholds to find all valid columns
        # Use more granular thresholds to catch columns at different densities
        for threshold_ratio in [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05]:
            # Find all runs (not just the longest)
            if search_sum_x.size == 0:
                continue
            max_val = search_sum_x.max()
            if max_val == 0:
                continue
            threshold = max(1, threshold_ratio * float(max_val))
            indices = np.where(search_sum_x > threshold)[0]
            if indices.size == 0:
                continue
            
            # Find all continuous runs
            splits = np.where(np.diff(indices) > 1)[0]
            starts = [indices[0]]
            ends = []
            for idx in splits:
                ends.append(indices[idx])
                starts.append(indices[idx + 1])
            ends.append(indices[-1])
            
            # Process each run as a potential column
            for start, end in zip(starts, ends):
                x0_cand = start
                x1_cand = end + 1
                w_cand = x1_cand - x0_cand
                
                # Check if width is reasonable for a column (allow wider range to find all columns)
                # Minimum width can be smaller to catch first column, maximum can be larger
                min_col_width = max(300, VERTICAL_WIDTH_RANGE[0] - 400)  # Allow even narrower columns (300px min)
                max_col_width = min(VERTICAL_WIDTH_RANGE[1] + 500, int(width * 0.75))  # Allow wider columns
                if min_col_width <= w_cand <= max_col_width:
                    density = search_sum_x[x0_cand:x1_cand].sum()
                    ideal_width = (VERTICAL_WIDTH_RANGE[0] + VERTICAL_WIDTH_RANGE[1]) / 2
                    width_score = 1.0 / (1.0 + abs(w_cand - ideal_width) / 200)
                    # Prefer columns that are not too close to left edge (x0 > 50) to avoid first column
                    position_score = 1.0 if x0_cand > 50 else 0.7
                    score = density * width_score * position_score
                    all_columns.append((x0_cand, x1_cand, w_cand, score))
        
            # Remove duplicates and sort by x position
            filtered_columns = []  # Initialize outside the if block
            if all_columns:
                # Sort by x0 position (left to right)
                all_columns.sort(key=lambda c: c[0])
                # Remove overlapping columns (keep the one with higher score)
                # Use stricter overlap detection (30% instead of 50%) to keep more distinct columns
                for col in all_columns:
                    x0, x1, w, score = col
                    overlap = False
                    for existing in filtered_columns:
                        ex0, ex1 = existing[0], existing[1]
                        # Check if columns overlap significantly (>30%)
                        overlap_size = max(0, min(x1, ex1) - max(x0, ex0))
                        if overlap_size > min(w, ex1 - ex0) * 0.3:
                            overlap = True
                            # Replace if this one has higher score
                            if score > existing[3]:
                                filtered_columns.remove(existing)
                                filtered_columns.append(col)
                            break
                    if not overlap:
                        filtered_columns.append(col)
            
            # Sort again by x position if we have columns
            if filtered_columns:
                filtered_columns.sort(key=lambda c: c[0])
            
            # CRITICAL: Must find at least 2 columns to select the second one
            if len(filtered_columns) < 2:
                logger.info("Projection detection: found only %d column(s), need at least 2 to select second.", len(filtered_columns))
                # If we found 1 column but it's wide, try to split it into multiple columns
                if len(filtered_columns) == 1:
                    x0_single, x1_single, w_single, _ = filtered_columns[0]
                    # If the single column is very wide (>1200px), it might contain multiple columns
                    if w_single > 1200:
                        logger.info("Single column is very wide (w=%d), attempting to split into multiple columns.", w_single)
                        # CRITICAL: Second column typically starts around 400-500px from left edge
                        # If the wide column starts very close to left (x0 < 100), it likely includes first column
                        # Use a safer split point: start second column at 400px or 25% of page width
                        if x0_single < 100:
                            # Wide column starting near left edge - second column starts around 400-500px
                            split_x = max(400, int(width * 0.25))
                        else:
                            # Column starts further right - use proportional split
                            split_x = max(x0_single + 400, int(x0_single + w_single * 0.3))
                        
                        # Ensure the second column has sufficient width (at least 800px)
                        w_second = x1_single - split_x
                        if w_second < 800:
                            # Adjust split point to ensure minimum width
                            split_x = max(x0_single, x1_single - 1100)  # Ensure at least 1100px width
                            # But don't go too far left (second column should start >= 400px)
                            split_x = max(400, split_x)
                            w_second = x1_single - split_x
                        
                        # Create second column
                        x0, x1, w = split_x, x1_single, w_second
                        logger.info("Projection detection: split wide column, using second part (x=%d, w=%d)", x0, w)
                        x_span = (x0, x1, w)
                    else:
                        logger.info("Single column is not wide enough to split. Rejecting.")
                        x_span = None
                else:
                    x_span = None
            else:
                # Select second column from left
                x0, x1, w, _ = filtered_columns[1]  # Second column
                logger.info("Projection detection: found %d columns, selecting second from left (x=%d)", 
                           len(filtered_columns), x0)
                x_span = (x0, x1, w)
        
        # Fallback: try sliding window approach if no columns found
        if x_span is None:
            # Try to find the best region using sliding window
            target_width = (VERTICAL_WIDTH_RANGE[0] + VERTICAL_WIDTH_RANGE[1]) // 2
            best_start = 0
            best_density = 0
            best_width = target_width
            
            for test_width in range(VERTICAL_WIDTH_RANGE[0], min(VERTICAL_WIDTH_RANGE[1] + 200, search_end), 25):
                for start_idx in range(0, max(1, len(search_sum_x) - test_width + 1)):
                    end_idx = start_idx + test_width
                    if end_idx > len(search_sum_x):
                        continue
                    window_density = search_sum_x[start_idx:end_idx].sum()
                    # Prefer regions closer to left edge
                    left_bonus = 1.0 / (1.0 + start_idx / 150.0)
                    # Prefer widths closer to target
                    width_bonus = 1.0 / (1.0 + abs(test_width - target_width) / 150.0)
                    score = window_density * left_bonus * width_bonus
                    if score > best_density:
                        best_density = score
                        best_start = start_idx
                        best_width = test_width
            
            if best_density > 0:
                x_span = (best_start, best_start + best_width, best_width)
            else:
                # Fallback: use longest run, but if it's too wide, split it
                x_span = longest_run(search_sum_x, 0.02)
                if x_span is None:
                    return None
                # If the longest run is very wide (>1200px), it might contain multiple columns
                # Split it to get the second column
                x0_long, x1_long, w_long = x_span
                if w_long > 1200:
                    logger.info("Longest run is very wide (w=%d), splitting to find second column.", w_long)
                    # CRITICAL: Second column typically starts around 400-500px from left edge
                    # If the wide region starts very close to left (x0 < 100), it likely includes first column
                    if x0_long < 100:
                        # Wide region starting near left edge - second column starts around 400px
                        split_x = max(400, int(width * 0.25))
                    else:
                        # Region starts further right - use proportional split
                        split_x = max(x0_long + 400, int(x0_long + w_long * 0.3))
                    
                    # Ensure the second column has sufficient width (at least 800px)
                    w_second = x1_long - split_x
                    if w_second < 800:
                        # Adjust split point to ensure minimum width
                        split_x = max(x0_long, x1_long - 1100)  # Ensure at least 1100px width
                        # But don't go too far left (second column should start >= 400px)
                        split_x = max(400, split_x)
                        w_second = x1_long - split_x
                    
                    # Use the second part as the column
                    x_span = (split_x, x1_long, w_second)
                    logger.info("Split wide region, using second part: x=%d, w=%d", x_span[0], x_span[2])
        
        y_span = longest_run(sum_y, 0.02)
        if y_span is None:
            return None

        x0, x1, w_span = x_span if len(x_span) == 3 else (x_span[0], x_span[1], x_span[1] - x_span[0])
        y0, y1, _ = y_span

        w = int(x1 - x0)
        h = int(y1 - y0)
        if w <= 0 or h <= 0:
            return None
        
        # CRITICAL: If the detected region is wider than expected for a single column (>1200px),
        # it likely includes multiple columns. Split it to get just the second column.
        if w > 1200 or (w > 900 and x0 < 100):  # Wide region OR wide region starting too close to left (likely includes first column)
            logger.info("Detected region is too wide (w=%d, x=%d), splitting to find second column.", w, x0)
            # CRITICAL: Second column typically starts around 400-500px from left edge
            # For john1, we need to be more careful - second column starts around 400-500px
            # If starting very close to left (x0 < 100), the second column starts around 400-500px
            if x0 < 100:
                # For wide regions starting at x=0, second column typically starts at 400-500px
                # Use a more conservative estimate: 450px or 27% of page width
                split_x = max(450, int(width * 0.27))
            else:
                split_x = max(x0 + 400, int(x0 + w * 0.3))
            
            # Ensure the second column has sufficient width (at least 900px) to avoid cutting text on right
            # But also ensure we don't go beyond 90% of page width
            max_right = min(width * 0.9, x1)
            w_second = max_right - split_x
            
            if w_second < 900:
                # Try to expand width by adjusting split point
                # Calculate how much we can expand
                ideal_width = 1000  # Ideal width for Hebrew column
                needed_split_x = max_right - ideal_width
                # But don't go too far left (second column should start >= 400px)
                split_x = max(400, needed_split_x)
                w_second = max_right - split_x
                # If still not enough, use maximum available
                if w_second < 800:
                    split_x = max(400, max_right - 1100)
                    w_second = max_right - split_x
            
            x0 = split_x
            w = min(w_second, 1100)  # Cap at 1100px
            x1 = x0 + w
            logger.info("Split wide region, using second part: x=%d, w=%d (ensuring sufficient width)", x0, w)
        
        # If width is too narrow, try to expand it (but stay within left-center region)
        if w < VERTICAL_WIDTH_RANGE[0]:
            # Try expanding to the right if possible
            max_expand = min(VERTICAL_WIDTH_RANGE[0], search_end - x0)
            if max_expand >= VERTICAL_WIDTH_RANGE[0]:
                w = VERTICAL_WIDTH_RANGE[0]
                x1 = x0 + w
            else:
                # Can't expand enough, try to find a better starting position
                # Look for a region starting earlier that can achieve minimum width
                if x0 > VERTICAL_X_RANGE[0]:
                    # Try starting from expected x position
                    new_x0 = max(0, VERTICAL_X_RANGE[0] - 50)
                    if new_x0 + VERTICAL_WIDTH_RANGE[0] <= search_end:
                        x0 = new_x0
                        w = VERTICAL_WIDTH_RANGE[0]
                        x1 = x0 + w
                    else:
                        logger.info("Projection detection: cannot achieve minimum width, rejecting.")
                        return None
                else:
                    logger.info("Projection detection: width too narrow and cannot expand, rejecting.")
                    return None
        
        # Expand vertical range to cover most of the page (start from top, end near bottom)
        # CRITICAL: ALWAYS start from very top (y=0 or small margin <50px) to preserve enumeration/verse numbers
        # Ignore the detected y0 position - we need the full column from top
        # The Hebrew column typically spans most of the page height (85-95%)
        y0_start = max(0, min(50, int(height * 0.02)))  # Start from top, max 50px margin (2% of height)
        # Extend to near bottom (90-95% of page to ensure we capture all text)
        y1_end = min(height - 1, int(height * 0.93))  # Extend to 93% of page
        h = y1_end - y0_start
        
        # Ensure we capture enough height (at least 85% of page for full text)
        min_height = int(height * 0.85)
        if h < min_height:
            # Expand downward if possible
            y1_end = min(height - 1, y0_start + min_height)
            h = y1_end - y0_start
        
        y0 = y0_start
        y1 = y1_end

        # CRITICAL: If the detected width is too large, find the leftmost dense sub-region
        # Hebrew column should be narrow (800-1200px), not the full page width
        max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(width * 0.6))
        if w > max_allowed_width:
            # Find the leftmost dense region within expected width
            # Search in the left-center region (first 50% of page)
            search_end = min(int(width * 0.5), len(sum_x))
            search_sum_x = sum_x[:search_end]
            
            if search_sum_x.size > 0:
                # Use sliding window to find best leftmost region of expected width
                # Target width: around 1000-1100px (middle of expected range)
                target_width = (VERTICAL_WIDTH_RANGE[0] + VERTICAL_WIDTH_RANGE[1]) // 2
                best_start = 0
                best_density = 0
                best_width = target_width
                
                # Try different widths around the target
                for test_width in range(VERTICAL_WIDTH_RANGE[0], min(max_allowed_width + 1, search_end), 50):
                    for start_idx in range(0, max(1, len(search_sum_x) - test_width + 1)):
                        end_idx = start_idx + test_width
                        if end_idx > len(search_sum_x):
                            continue
                        window_density = search_sum_x[start_idx:end_idx].sum()
                        # Prefer regions closer to left edge (penalize distance from left)
                        left_bonus = 1.0 / (1.0 + start_idx / 100.0)
                        score = window_density * left_bonus
                        if score > best_density:
                            best_density = score
                            best_start = start_idx
                            best_width = test_width
                
                x0 = best_start
                x1 = best_start + best_width
                w = best_width
                
                # Ensure width is at least minimum
                if w < VERTICAL_WIDTH_RANGE[0]:
                    if x0 + VERTICAL_WIDTH_RANGE[0] <= search_end:
                        w = VERTICAL_WIDTH_RANGE[0]
                        x1 = x0 + w
                    else:
                        logger.info("Projection detection: cannot achieve minimum width, rejecting.")
                        return None
            else:
                # Fallback: use expected position and width from left edge
                x0 = max(0, VERTICAL_X_RANGE[0] - 50)
                w = min(VERTICAL_WIDTH_RANGE[1] + 100, max_allowed_width)
                x1 = x0 + w

        # Ensure width is within reasonable bounds for Hebrew column
        w = min(w, max_allowed_width)
        # STRICTER: Ensure minimum width of 800px
        if w < VERTICAL_WIDTH_RANGE[0]:
            # Try to expand from left edge if possible
            if x0 + VERTICAL_WIDTH_RANGE[0] <= width * 0.5:
                w = VERTICAL_WIDTH_RANGE[0]
                x1 = x0 + w
            else:
                logger.info("Projection detection: cannot achieve minimum width, rejecting.")
                return None
        
        # Ensure coordinates are within image bounds
        # Hebrew column should not start at x=0 (there's usually a margin)
        x0 = max(50, int(x0))  # Minimum 50px from left edge
        y0 = max(0, int(y0))
        
        # Ensure width fits within image
        if x0 + w > width:
            x0 = max(0, width - w)
            w = width - x0
        
        # Ensure height fits within image (but try to preserve the expanded height)
        if y0 + h > height:
            # Try to keep the expanded height by adjusting y0 upward if possible
            if h <= height:
                y0 = max(0, height - h)
            else:
                # If height is larger than image, reduce it but keep as much as possible
                h = height - y0
        
        # Final bounds check
        w = min(w, width - x0)
        h = min(h, height - y0)

        box = (x0, y0, w, h)
        
        # Validate the detected box - ensure it's in reasonable position and size
        x, y, w, h = box
        center_x = x + w / 2
        
        # CRITICAL VALIDATION: Hebrew column should be narrow, not the entire page width
        # Maximum width: 1400px OR 60% of page width, whichever is smaller
        max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(width * 0.6))
        if w > max_allowed_width:
            logger.info("Projection-based detection found box too wide (w=%d, max=%d, page_width=%d), rejecting.", w, max_allowed_width, width)
            return None
        
        # The Hebrew column should be in the left-center region
        if center_x > width * 0.5:
            logger.info("Projection-based detection found column too far right (center_x=%.1f), rejecting.", center_x)
            return None
        
        # Also check that the left edge is not too far right
        if x > width * 0.4:
            logger.info("Projection-based detection found column starting too far right (x=%d), rejecting.", x)
            return None
        
        # STRICTER: Ensure minimum width of 800px for a valid Hebrew column
        if w < VERTICAL_WIDTH_RANGE[0]:
            logger.info("Projection-based detection found box too narrow (w=%d, min=%d), rejecting.", 
                       w, VERTICAL_WIDTH_RANGE[0])
            return None
        
        # CRITICAL: Reject columns starting at x=0 or too close to left edge (likely first column)
        if x < 50:
            logger.info("Projection-based detection found column starting too close to left edge (x=%d, likely first column), rejecting.", x)
            return None
        
        logger.info(
            "Projection-based column: x=%d, y=%d, w=%d, h=%d",
            box[0],
            box[1],
            box[2],
            box[3],
        )
        return box

    def _is_box_reasonable(self, box: Tuple[int, int, int, int], image_shape: Tuple[int, int, int]) -> bool:
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
        
        # CRITICAL: Hebrew column should be narrow, not the entire page width
        max_allowed_width = min(VERTICAL_WIDTH_RANGE[1] + 200, int(img_w * 0.6))
        
        # Width validation: allow some flexibility for detected columns
        # Minimum can be 600px (if detected), ideal is 800-1200px, max is 1400px or 60% of page
        min_allowed_width = max(600, VERTICAL_WIDTH_RANGE[0] - 200)  # Allow narrower if detected
        width_ok_min = w >= min_allowed_width  # Minimum 600px (flexible)
        width_ok_max = w <= max_allowed_width  # Reject if too wide (entire page)
        width_ok = width_ok_min and width_ok_max
        
        # Height validation: should be at least 40% of image height or 1500px minimum
        min_height_required = max(int(img_h * 0.4), 1500)
        height_ok = h >= min_height_required
        
        # Position validation: must be within image bounds
        within_bounds = x >= 0 and y >= 0 and x + w <= img_w and y + h <= img_h
        
        # Position validation: should be in left-center region
        # CRITICAL: Hebrew column is second from left, so it should NOT start at x=0 (that's first column)
        # According to prompt: second column typically starts at 200-600px from left edge
        # Validation: x <= 35% of page width OR x <= 600px (whichever is more permissive)
        center_x = x + w / 2
        max_x_percent = int(img_w * 0.35)  # 35% of page width
        max_x_absolute = 600  # Absolute max 600px as per prompt
        max_x = max(max_x_percent, max_x_absolute)  # Use more permissive limit
        position_ok = (center_x <= img_w * 0.50 and  # Center before 50% of page
                      x <= max_x and  # Start before 35% of page or 600px
                      x >= 50)  # Minimum 50px from left edge (reject first column at x=0)
        
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

        candidates: List[Tuple[int, int, int, int]] = []
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

    def detect_hebrew_column(self, image: cv2.Mat) -> Tuple[int, int, int, int]:
        """
        Dynamically detect the Hebrew text column using contours and line detection.

        Args:
            image: OpenCV image matrix

        Returns:
            Tuple (x, y, w, h) of the bounding box
        """
        height, width = image.shape[:2]
        if height == 0 or width == 0:
            fallback = get_fallback_coords(width, height)
            return (
                fallback["x"],
                fallback["y"],
                fallback["w"],
                fallback["h"],
            )

        gray, thresh = self._preprocess(image)

        box = self._find_main_box_from_contours(thresh)
        if box is None:
            logger.info("Contour detection failed; trying Hough lines.")
            box = self._find_main_box_with_hough(gray, thresh)
        if box is None:
            logger.info("Hough detection failed; trying projection-based search.")
            box = self._find_main_box_from_projection(thresh)

        if box is None:
            logger.warning("No suitable column detected. Using fallback coordinates.")
            fallback = get_fallback_coords(width, height)
            return (
                fallback["x"],
                fallback["y"],
                fallback["w"],
                fallback["h"],
            )

        if not self._is_box_reasonable(box, image.shape):
            logger.info("Detected box out of expected range; refining with projection.")
            refined_box = self._find_main_box_from_projection(thresh)
            if refined_box is not None and self._is_box_reasonable(refined_box, image.shape):
                box = refined_box
        
        # Additional validation: ensure x is reasonable (second column typically 200-600px from left)
        x, y, w, h = box
        # According to prompt: second column typically starts at 200-600px from left edge
        max_x_percent = int(width * 0.35)  # 35% of page width
        max_x_absolute = 600  # Absolute max 600px as per prompt
        max_x = max(max_x_percent, max_x_absolute)  # Use more permissive limit
        if x > max_x:  # Hebrew column should start before 35% of page or 600px
            logger.info("Box starts too far right (x=%d, max=%d), trying projection.", 
                       x, max_x)
            refined_box = self._find_main_box_from_projection(thresh)
            if refined_box is not None and self._is_box_reasonable(refined_box, image.shape):
                box = refined_box
            else:
                logger.warning("Projection also failed or unreasonable. Using fallback.")
                fallback = get_fallback_coords(width, height)
                return (
                    fallback["x"],
                    fallback["y"],
                    fallback["w"],
                    fallback["h"],
                )
        
        if not self._is_box_reasonable(box, image.shape):
            logger.warning("Unable to find a reasonable box. Using fallback coordinates.")
            fallback = get_fallback_coords(width, height)
            return (
                fallback["x"],
                fallback["y"],
                fallback["w"],
                fallback["h"],
            )

        title_box = self._detect_title_region(thresh, box)
        if title_box:
            tx, ty, tw, th = title_box
            x, y, w, h = box
            new_x = min(x, tx)
            # CRITICAL: Always keep y=0 to preserve enumeration/title at top
            new_y = 0  # Force y=0, don't let title detection move it up
            new_w = max(x + w, tx + tw) - new_x
            new_h = max(y + h, ty + th) - new_y
            box = (new_x, new_y, new_w, new_h)
        else:
            # CRITICAL: Ensure y=0 even if no title detected
            x, y, w, h = box
            box = (x, 0, w, h)
        
        # CRITICAL: Final check - if box is too wide (>900px) or starts too close to left (x < 150),
        # split it to get just the second column
        x, y, w, h = box
        logger.debug("Before final check: x=%d, w=%d", x, w)
        if w > 900 or (w > 800 and x < 150):  # More permissive condition
            logger.info("Final box is too wide (w=%d, x=%d), splitting to get second column.", w, x)
            # Second column typically starts around 400-500px from left edge
            if x < 150:
                new_x = max(400, int(width * 0.25))  # Start around 25-30% of page width
            else:
                new_x = max(x + 400, int(x + w * 0.3))
            x = new_x
            w = min(1100, width - x)  # Limit width to reasonable size
            box = (x, y, w, h)
            logger.info("Split final box, using second part: x=%d, w=%d", x, w)

        logger.info("Final bounding box: x=%d, y=%d, w=%d, h=%d", box[0], box[1], box[2], box[3])
        return box

    def _is_image_blank(self, image: np.ndarray) -> bool:
        """
        Check if an image is blank or has very little content.
        
        Args:
            image: BGR image
            
        Returns:
            True if image appears to be blank
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Calculate standard deviation - blank images have low std
        std = np.std(gray)
        # Blank images typically have std < 10-15
        return std < 15
    
    def process_single_image(self, image_path: Path) -> bool:
        """
        Process a single image: load, detect, crop, and save.

        Args:
            image_path: Path to the input image

        Returns:
            True if successful, False otherwise
        """
        try:
            image_number = int(image_path.stem)
            
            # Special handling for john1
            if self.is_john1:
                # Skip specific images that are not part of the manuscript
                if image_number in [6, 8]:
                    logger.info(f"Skipping {image_path.name} (not part of manuscript for john1)")
                    return False
                # From 000009.png onwards, process only odd-numbered images
                if image_number >= 9:
                    if image_number % 2 == 0:
                        logger.info(f"Skipping even-numbered image {image_path.name} (john1: only odd from 000009 onwards)")
                        return False
                # For images before 000009, process only even-numbered (normal behavior)
                elif image_number % 2 == 1:
                    logger.info(f"Skipping odd-numbered image {image_path.name} (typically no Hebrew text)")
                    return False
            else:
                # Normal behavior: skip odd-numbered images
                if image_number % 2 == 1:
                    logger.info(f"Skipping odd-numbered image {image_path.name} (typically no Hebrew text)")
                    return False
            
            # Read the image
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return False

            # Check if image is blank
            if self._is_image_blank(image):
                logger.info(f"Skipping blank image {image_path.name}")
                return False

            height, width = image.shape[:2]

            # Detect bounding box
            x, y, w, h = self.detect_hebrew_column(image)

            # Validate and clamp coordinates to image boundaries
            x = min(max(0, x), max(0, width - 1))
            # CRITICAL: Always start from top (y=0) to preserve enumeration/title/verse numbers
            y = 0  # Force y to be 0 to preserve all top content
            w = max(1, min(w, width - x))
            
            # CRITICAL: If the box is still too wide (>900px) or starts too close to left (x < 150),
            # it likely includes the first column. Split it to get just the second column.
            if w > 900 or (w > 800 and x < 150):  # More permissive condition
                logger.info("Final box in process_single_image is too wide (w=%d, x=%d), splitting to get second column.", w, x)
                # Second column typically starts around 400-500px from left edge
                if x < 150:
                    new_x = max(400, int(width * 0.25))  # Start around 25-30% of page width
                else:
                    new_x = max(x + 400, int(x + w * 0.3))
                x = new_x
                w = min(1100, width - x)  # Limit width to reasonable size
                logger.info("Split final box in process_single_image, using second part: x=%d, w=%d", x, w)
            
            # Ensure height covers most of the page (85-95%)
            min_height = int(height * 0.85)
            h = max(min_height, min(h, height - y))

            # Crop
            cropped = image[y:y+h, x:x+w]

            # Create output path
            output_filename = image_path.name
            output_path = self.output_dir / output_filename
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Save
            success = cv2.imwrite(str(output_path), cropped)
            if not success:
                logger.error(f"Failed to save cropped image: {output_path}")
                return False

            logger.info(f"Saved cropped image to {output_path} (Box: {x},{y},{w},{h})")
            return True

        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
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
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.tiff', '*.bmp']:
            image_files.extend(self.input_dir.glob(ext))
        # Case insensitive search would be better but glob is case sensitive on Linux
        # Adding uppercase extensions just in case
        for ext in ['*.PNG', '*.JPG', '*.JPEG']:
            image_files.extend(self.input_dir.glob(ext))
            
        image_files = sorted(list(set(image_files))) # Remove duplicates and sort

        if not image_files:
            logger.warning(f"No image files found in {self.input_dir}")
            return 0, 0

        logger.info(f"Found {len(image_files)} images to process in {self.input_dir}")

        successful = 0
        with tqdm(total=len(image_files), desc="Processing images") as pbar:
            for image_path in image_files:
                if self.process_single_image(image_path):
                    successful += 1
                pbar.update(1)

        logger.info(f"Processing complete: {successful}/{len(image_files)} images processed successfully")
        return successful, len(image_files)

def main():
    parser = argparse.ArgumentParser(description="Extract Hebrew text columns from images.")
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/images/philemon",
        help="Directory containing input images",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/temp/philemon",
        help="Directory to save cropped images",
    )

    args = parser.parse_args()
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)

    logger.info(f"Input Directory: {input_path}")
    logger.info(f"Output Directory: {output_path}")

    extractor = HebrewTextExtractor(input_path, output_path)
    extractor.process_all_images()

if __name__ == "__main__":
    main()






