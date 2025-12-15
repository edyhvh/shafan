#!/usr/bin/env python3
"""
Apply final improved find_boundary fix to all problematic images.

This script processes all images mentioned by the user with the improved
solution that detects and avoids first column capture.
"""

import cv2
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent))

from scripts.hebrew_images.extractor import HebrewTextExtractor


def analyze_box_for_first_column(thresh, box):
    """Analyze if box contains first column."""
    x, y, w, h = box
    height, width = thresh.shape[:2]
    
    if x < 250 and w > 1000:
        left_region = thresh[y:y+h, x:min(x+150, x+w)]
        if left_region.size > 0:
            left_density = np.sum(left_region > 0) / left_region.size
            if left_density > 0.15:
                for check_x in range(300, min(450, width - 800), 20):
                    check_region = thresh[y:y+h, check_x:check_x+100]
                    if check_region.size > 0:
                        check_density = np.sum(check_region > 0) / check_region.size
                        if 0.10 < check_density < 0.30:
                            return True, check_x, left_density
                return True, 350, left_density
    
    # Check high density
    check_width = min(150, w)
    left_region = thresh[y:y+h, x:x+check_width]
    if left_region.size > 0:
        density = np.sum(left_region > 0) / left_region.size
        if density > 0.25:
            before_start = max(0, x - 100)
            before_region = thresh[y:y+h, before_start:x]
            if before_region.size > 0:
                before_density = np.sum(before_region > 0) / before_region.size
                if before_density > 0.10:
                    for check_x in range(max(300, x), min(x + 200, width), 20):
                        check_region = thresh[y:y+h, check_x:check_x+80]
                        if check_region.size > 0:
                            check_density = np.sum(check_region > 0) / check_region.size
                            if 0.12 < check_density < 0.30:
                                return True, check_x, density
                    return True, max(300, x + 100), density
    
    return False, x, 0.0


def find_text_left_boundary(thresh, current_x, search_width=150):
    """Find Hebrew text left boundary."""
    height = thresh.shape[0]
    search_start = max(0, current_x - search_width)
    search_end = current_x
    
    if search_end <= search_start:
        return current_x
    
    search_region = thresh[:, search_start:search_end]
    if search_region.size == 0:
        return current_x
    
    projection = search_region.sum(axis=0)
    if projection.size == 0 or projection.max() == 0:
        return current_x
    
    threshold = projection.max() * 0.15
    text_start_idx = None
    for i in range(len(projection) - 1, -1, -1):
        if projection[i] > threshold:
            text_start_idx = i
            break
    
    if text_start_idx is None:
        return current_x
    
    text_start_abs = search_start + text_start_idx
    return max(0, text_start_abs - 30)


def apply_fix(image_path, extractor, output_dir):
    """Apply final fix to image."""
    image = cv2.imread(str(image_path))
    if image is None:
        return None
    
    height, width = image.shape[:2]
    gray, thresh = extractor._preprocess(image)
    (x, y, w, h), method = extractor.detect_hebrew_column(image, img_logger=None)
    
    # Check for first column
    has_first_col, adjusted_x, left_density = analyze_box_for_first_column(thresh, (x, y, w, h))
    
    if has_first_col:
        x = adjusted_x
        w = min(width - x, w - (adjusted_x - x))
    
    # Find text boundary
    safe_x = find_text_left_boundary(thresh, x, search_width=150)
    expand_amount = x - safe_x
    
    # Limit expansion
    max_expansion = 80
    if expand_amount > max_expansion:
        safe_x = max(0, x - max_expansion)
        expand_amount = max_expansion
    
    # Bottom padding
    check_start = min(y + h, height - 1)
    check_end = min(y + h + 100, height)
    
    if check_end > check_start:
        beyond_bottom_region = thresh[check_start:check_end, x:x+w]
        if beyond_bottom_region.size > 0:
            beyond_bottom_density = np.sum(beyond_bottom_region > 0) / beyond_bottom_region.size
            if beyond_bottom_density > 0.05:
                if beyond_bottom_density > 0.15:
                    bottom_expand = 120
                elif beyond_bottom_density > 0.10:
                    bottom_expand = 100
                else:
                    bottom_expand = 80
                new_h = min(height - y, h + bottom_expand)
            else:
                new_h = min(height - y, h + 100)
        else:
            new_h = min(height - y, h + 100)
    else:
        new_h = min(height - y, h + 100)
    
    new_w = min(width - safe_x, w + expand_amount)
    
    # Crop and save
    fixed_crop = image[y:y+new_h, safe_x:safe_x+new_w]
    fixed_path = output_dir / f"{image_path.stem}_fixed.png"
    cv2.imwrite(str(fixed_path), fixed_crop)
    
    return {
        'image': image_path.name,
        'original_x': x,
        'fixed_x': safe_x,
        'has_first_col': has_first_col,
    }


def main():
    """Process all problematic images."""
    output_dir = Path("data/temp/all_problematic_fixed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    problematic_images = [
        # matthew
        ("data/images/raw_images/matthew/000006.png", "matthew"),
        ("data/images/raw_images/matthew/000240.png", "matthew"),
        ("data/images/raw_images/matthew/000274.png", "matthew"),
        
        # mark
        ("data/images/raw_images/mark/000012.png", "mark"),
        ("data/images/raw_images/mark/000024.png", "mark"),
        ("data/images/raw_images/mark/000026.png", "mark"),
        ("data/images/raw_images/mark/000068.png", "mark"),
        ("data/images/raw_images/mark/000098.png", "mark"),
        ("data/images/raw_images/mark/000128.png", "mark"),
        ("data/images/raw_images/mark/000154.png", "mark"),
        ("data/images/raw_images/mark/000160.png", "mark"),
        ("data/images/raw_images/mark/000162.png", "mark"),
        ("data/images/raw_images/mark/000166.png", "mark"),
        ("data/images/raw_images/mark/000178.png", "mark"),
        ("data/images/raw_images/mark/000180.png", "mark"),
        ("data/images/raw_images/mark/000182.png", "mark"),
        
        # luke
        ("data/images/raw_images/luke/000010.png", "luke"),
        ("data/images/raw_images/luke/000042.png", "luke"),
        ("data/images/raw_images/luke/000102.png", "luke"),
        ("data/images/raw_images/luke/000130.png", "luke"),
        ("data/images/raw_images/luke/000226.png", "luke"),
        ("data/images/raw_images/luke/000256.png", "luke"),
        ("data/images/raw_images/luke/000258.png", "luke"),
        
        # john
        ("data/images/raw_images/john/000142.png", "john"),
    ]
    
    print("="*80)
    print("Processing All Problematic Images")
    print("="*80)
    
    results = []
    
    for img_path_str, book in problematic_images:
        img_path = Path(img_path_str)
        if not img_path.exists():
            print(f"  WARNING: {img_path.name} not found")
            continue
        
        input_dir = Path(f"data/images/raw_images/{book}")
        extractor = HebrewTextExtractor(input_dir, output_dir)
        
        result = apply_fix(img_path, extractor, output_dir)
        if result:
            results.append(result)
            status = "⚠️ First col" if result['has_first_col'] else "✓ OK"
            print(f"  {img_path.name}: x={result['original_x']} -> {result['fixed_x']} {status}")
    
    print(f"\nProcessed: {len(results)} images")
    print(f"Results saved in: {output_dir}")
    print("\nReview the fixed images to verify they look correct.")


if __name__ == "__main__":
    main()
