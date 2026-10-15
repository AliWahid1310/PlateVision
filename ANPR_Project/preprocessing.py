"""
preprocessing.py — Image Preprocessing Module
================================================
This module handles all image preprocessing steps needed before
we can detect a number plate. Each function does ONE thing clearly.

WHY DO WE PREPROCESS?
Raw camera images contain noise, color information, and varying sizes.
Preprocessing simplifies the image so that plate detection becomes easier.
Think of it like cleaning a dirty window before trying to read text through it.
"""

import cv2
import numpy as np
import os


def read_image(image_path):
    """
    Read an image from disk using OpenCV.
    
    OpenCV reads images in BGR (Blue-Green-Red) format by default,
    which is different from the usual RGB. This doesn't matter for
    processing but matters if you display with matplotlib.
    
    Returns:
        image (numpy array) or None if the file doesn't exist
    """
    # Check if the file actually exists
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        return None
    
    # cv2.imread() reads the image as a NumPy array
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"[ERROR] Could not read image: {image_path}")
        return None
    
    print(f"[INFO] Image loaded successfully: {image_path}")
    print(f"[INFO] Image shape: {image.shape}")  # (height, width, channels)
    return image


def resize_image(image, target_width=800):
    """
    Resize the image to a standard width while keeping the aspect ratio.
    
    WHY RESIZE?
    - Different cameras produce different image sizes
    - Very large images are slow to process
    - Very small images may lose detail
    - A consistent size makes our contour filtering more reliable
    
    We keep the aspect ratio so the image doesn't get distorted.
    """
    height, width = image.shape[:2]
    
    # Only resize if the image is wider than our target
    if width <= target_width:
        return image
    
    # Calculate the new height to maintain aspect ratio
    # ratio = new_width / old_width
    ratio = target_width / width
    new_height = int(height * ratio)
    
    # cv2.resize() scales the image
    # cv2.INTER_AREA is best for shrinking images (avoids aliasing)
    resized = cv2.resize(image, (target_width, new_height), interpolation=cv2.INTER_AREA)
    
    print(f"[INFO] Image resized from ({width}x{height}) to ({target_width}x{new_height})")
    return resized


def convert_to_grayscale(image):
    """
    Convert a color (BGR) image to grayscale.
    
    WHY GRAYSCALE?
    - Color information (red, green, blue) is not needed for edge detection
    - Grayscale has only 1 channel instead of 3, so it's faster to process
    - Most CV algorithms (Canny, threshold) work on single-channel images
    
    Each pixel in grayscale is a single value from 0 (black) to 255 (white).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print("[INFO] Converted to grayscale")
    return gray


def apply_gaussian_blur(gray_image, kernel_size=(5, 5)):
    """
    Apply Gaussian blur to reduce noise in the image.
    
    WHY BLUR?
    - Camera images contain random noise (tiny bright/dark dots)
    - Noise creates false edges that confuse edge detection
    - Gaussian blur smooths the image by averaging nearby pixels
    - The kernel_size controls how much blurring happens
      (5,5) means each pixel is averaged with its 5x5 neighborhood
    
    The kernel size must be ODD numbers (3, 5, 7, etc.)
    """
    blurred = cv2.GaussianBlur(gray_image, kernel_size, 0)
    print(f"[INFO] Applied Gaussian blur with kernel {kernel_size}")
    return blurred


def apply_edge_detection(blurred_image, low_threshold=50, high_threshold=200):
    """
    Apply Canny edge detection to find edges (boundaries) in the image.
    
    WHY EDGE DETECTION?
    - Number plates have clear rectangular edges
    - Canny finds pixels where brightness changes sharply
    - The result is a black-and-white image where edges are white
    
    HOW CANNY WORKS (simplified):
    1. Finds the gradient (rate of brightness change) at each pixel
    2. If gradient > high_threshold → definitely an edge
    3. If gradient < low_threshold → definitely NOT an edge
    4. If gradient is between the two → edge only if connected to a strong edge
    
    Low values (30, 100) detect more edges (including noise).
    High values (100, 300) detect fewer but stronger edges.
    """
    edges = cv2.Canny(blurred_image, low_threshold, high_threshold)
    print(f"[INFO] Applied Canny edge detection (thresholds: {low_threshold}, {high_threshold})")
    return edges


def apply_threshold(gray_image):
    """
    Apply binary thresholding to create a clean black-and-white image.
    
    WHY THRESHOLD?
    - Useful for OCR preprocessing (makes text stand out)
    - Converts every pixel to either pure black or pure white
    - cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU automatically finds
      the best threshold value using Otsu's method
    
    OTSU'S METHOD: Automatically calculates the optimal threshold
    by analyzing the histogram (distribution of pixel values).
    This is better than picking a fixed number manually.
    """
    # Otsu's method automatically determines the threshold value
    # THRESH_BINARY_INV makes the text white and background black
    _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    print("[INFO] Applied Otsu's binary thresholding")
    return thresh


def preprocess_image(image_path, save_dir=None):
    """
    Run the COMPLETE preprocessing pipeline on one image.
    
    Pipeline:
    1. Read the image
    2. Resize it
    3. Convert to grayscale
    4. Apply Gaussian blur
    5. Apply Canny edge detection
    6. Apply thresholding (for OCR later)
    
    Returns a dictionary with all versions of the image so other
    modules can use whichever version they need.
    """
    # Step 1: Read
    original = read_image(image_path)
    if original is None:
        return None
    
    # Step 2: Resize
    resized = resize_image(original)
    
    # Step 3: Grayscale
    gray = convert_to_grayscale(resized)
    
    # Step 4: Blur
    blurred = apply_gaussian_blur(gray)
    
    # Step 5: Edge detection
    edges = apply_edge_detection(blurred)
    
    # Step 6: Thresholding
    thresh = apply_threshold(gray)
    
    # Save intermediate images if a save directory is provided
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        cv2.imwrite(os.path.join(save_dir, f"{base_name}_gray.jpg"), gray)
        cv2.imwrite(os.path.join(save_dir, f"{base_name}_blurred.jpg"), blurred)
        cv2.imwrite(os.path.join(save_dir, f"{base_name}_edges.jpg"), edges)
        cv2.imwrite(os.path.join(save_dir, f"{base_name}_thresh.jpg"), thresh)
        print(f"[INFO] Preprocessing images saved to: {save_dir}")
    
    # Return all versions in a dictionary
    result = {
        "original": resized,       # Color image (resized)
        "gray": gray,              # Grayscale
        "blurred": blurred,        # Blurred grayscale
        "edges": edges,            # Edge-detected (for plate detection)
        "thresh": thresh,          # Thresholded (for OCR)
    }
    
    print("[INFO] Preprocessing complete!\n")
    return result


# ============================================
# Test this module independently
# ============================================
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python preprocessing.py <image_path>")
        print("Example: python preprocessing.py input_images/car1.jpg")
    else:
        result = preprocess_image(sys.argv[1], save_dir="output_images")
        if result:
            print("Preprocessing successful! Check output_images/ folder.")
