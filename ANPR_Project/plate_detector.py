"""
plate_detector.py — Number Plate Detection Module
====================================================
This module detects number plates using OpenCV contours.

HOW IT WORKS (simple explanation):
1. We already have an edge-detected image from preprocessing
2. We find "contours" — outlines of shapes in the edge image
3. Number plates are rectangular, so we look for 4-sided shapes
4. We filter by size and aspect ratio (plates are wider than tall)
5. The best matching rectangle is our number plate candidate

This is a SIMPLE approach. It works well on clear, front-facing photos
but may fail on angled, blurry, or partially hidden plates.
"""

import cv2
import numpy as np
import os


def find_contours(edge_image):
    """
    Find all contours (outlines) in the edge-detected image.
    
    WHAT IS A CONTOUR?
    - A contour is a curve joining all continuous points along a boundary
    - Think of it as drawing around the outline of an object
    - OpenCV finds these outlines automatically from edge images
    
    cv2.RETR_TREE: Retrieves all contours and their hierarchy
    cv2.CHAIN_APPROX_SIMPLE: Compresses the contour by removing
        redundant points (e.g., a straight line only needs 2 endpoints)
    """
    contours, _ = cv2.findContours(
        edge_image.copy(),
        cv2.RETR_TREE,              # Get all contours
        cv2.CHAIN_APPROX_SIMPLE     # Compress contour points
    )
    
    # Sort contours by area (largest first)
    # We do this because the plate is usually one of the larger rectangles
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
    
    print(f"[INFO] Found {len(contours)} contours (keeping top 30 by area)")
    return contours


def is_valid_plate(approx, image_shape):
    """
    Check if a contour could be a number plate based on its properties.
    
    A valid number plate candidate should:
    1. Have approximately 4 corners (it's a rectangle)
    2. Have a reasonable area (not too small, not too large)
    3. Have a reasonable aspect ratio (plates are wider than tall)
    
    Returns True if the contour looks like a plate, False otherwise.
    """
    # Must have 4 corners (rectangle)
    if len(approx) != 4:
        return False
    
    # Get the bounding rectangle
    x, y, w, h = cv2.boundingRect(approx)
    
    # Calculate aspect ratio (width / height)
    # Typical number plates have aspect ratio between 2.0 and 6.0
    # (they are 2x to 6x wider than they are tall)
    if h == 0:
        return False
    aspect_ratio = w / h
    
    # Calculate area
    area = cv2.contourArea(approx)
    image_area = image_shape[0] * image_shape[1]
    
    # Plate area should be between 0.5% and 15% of the image
    area_ratio = area / image_area
    
    # Check all conditions
    valid_aspect = 1.5 <= aspect_ratio <= 7.0
    valid_area = 0.005 <= area_ratio <= 0.15
    
    return valid_aspect and valid_area


def detect_plate(original_image, edge_image):
    """
    Detect the number plate in an image using contour analysis.
    
    ALGORITHM:
    1. Find all contours in the edge image
    2. For each contour, approximate its shape to a polygon
    3. If the polygon has 4 sides and passes our filters → it might be a plate
    4. Return the first valid match (since contours are sorted by size)
    
    WHY APPROXIMATE?
    cv2.approxPolyDP simplifies a contour to fewer points.
    epsilon controls how much simplification:
    - Small epsilon → keeps more detail
    - Large epsilon → more simplification
    We use 2% of the contour's perimeter as epsilon.
    
    Returns:
        plate_image: Cropped plate region (or None if not found)
        plate_coords: (x, y, w, h) of the plate (or None)
        annotated_image: Original image with plate rectangle drawn
    """
    # Make a copy so we don't modify the original
    annotated = original_image.copy()
    
    # Step 1: Find contours
    contours = find_contours(edge_image)
    
    plate_contour = None
    
    # Step 2: Loop through contours and find the plate
    for contour in contours:
        # Calculate the perimeter (total length of the contour)
        perimeter = cv2.arcLength(contour, closed=True)
        
        # Approximate the contour to a simpler polygon
        # epsilon = 2% of perimeter (controls simplification level)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, closed=True)
        
        # Step 3: Check if this contour looks like a plate
        if is_valid_plate(approx, original_image.shape):
            plate_contour = approx
            print("[INFO] Number plate candidate found!")
            break  # Take the first valid match
    
    # Step 4: If no plate was found, return None gracefully
    if plate_contour is None:
        print("[WARNING] No number plate detected in this image.")
        return None, None, annotated
    
    # Step 5: Get the bounding rectangle of the plate
    x, y, w, h = cv2.boundingRect(plate_contour)
    
    # Step 6: Crop the plate region from the original image
    plate_image = original_image[y:y+h, x:x+w]
    
    # Step 7: Draw a green rectangle around the plate on the annotated image
    cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 3)
    
    # Also draw the label "Number Plate"
    cv2.putText(
        annotated,
        "Number Plate",
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )
    
    plate_coords = (x, y, w, h)
    print(f"[INFO] Plate detected at: x={x}, y={y}, width={w}, height={h}")
    
    return plate_image, plate_coords, annotated


def save_plate(plate_image, save_path):
    """
    Save the cropped plate image to disk.
    
    This is useful for:
    - Debugging (you can visually check if the right region was cropped)
    - OCR input (the OCR module will read from this cropped image)
    """
    if plate_image is None:
        print("[WARNING] No plate image to save.")
        return False
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cv2.imwrite(save_path, plate_image)
    print(f"[INFO] Cropped plate saved to: {save_path}")
    return True


# ============================================
# Test this module independently
# ============================================
if __name__ == "__main__":
    import sys
    from preprocessing import preprocess_image
    
    if len(sys.argv) < 2:
        print("Usage: python plate_detector.py <image_path>")
        print("Example: python plate_detector.py input_images/car1.jpg")
    else:
        # Preprocess the image first
        result = preprocess_image(sys.argv[1])
        if result:
            # Detect the plate
            plate_img, coords, annotated = detect_plate(
                result["original"], result["edges"]
            )
            
            if plate_img is not None:
                save_plate(plate_img, "sample_data/detected_plate.jpg")
                cv2.imwrite("output_images/plate_detection_result.jpg", annotated)
                print("Plate detection complete! Check output_images/ folder.")
            else:
                print("No plate detected. Try a different image.")
