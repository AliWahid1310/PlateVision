"""
ocr.py — Optical Character Recognition Module
================================================
This module uses EasyOCR to read text from cropped number plate images.

WHAT IS OCR?
OCR (Optical Character Recognition) converts images of text into
actual text strings that a computer can understand. For example,
a photo of "ABC 1234" on a plate → the string "ABC1234".

WHY EasyOCR?
- Simple to use (just 2-3 lines of code)
- Supports 80+ languages
- Uses deep learning internally but we don't need to train anything
- Works reasonably well on clear plate images
- Free and open source
"""

import cv2
import numpy as np
import re

# EasyOCR is imported inside the function to avoid slow startup
# when this module is imported but OCR is not needed yet


def preprocess_plate_for_ocr(plate_image):
    """
    Preprocess the cropped plate image specifically for OCR.
    
    WHY SEPARATE PREPROCESSING FOR OCR?
    OCR works best when:
    - The image is grayscale (no distracting colors)
    - Text is dark on a light background (or vice versa)
    - The image is clean with minimal noise
    - The image is large enough to read characters
    
    Steps:
    1. Convert to grayscale
    2. Resize to make it larger (helps OCR read small text)
    3. Apply bilateral filter (reduces noise while keeping edges sharp)
    4. Apply thresholding (makes text stand out clearly)
    """
    # Step 1: Convert to grayscale if it's a color image
    if len(plate_image.shape) == 3:
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = plate_image.copy()
    
    # Step 2: Resize to make the plate larger (helps OCR accuracy)
    # We scale it to at least 300 pixels wide
    height, width = gray.shape
    if width < 300:
        scale = 300 / width
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Step 3: Bilateral filter
    # - Reduces noise while keeping edges sharp
    # - Better than Gaussian blur for text images
    # Parameters: (diameter, sigmaColor, sigmaSpace)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    
    # Step 4: Otsu's thresholding
    # Automatically finds the best threshold to separate text from background
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    print("[INFO] Plate preprocessed for OCR")
    return thresh


def clean_ocr_text(raw_text):
    """
    Clean the raw OCR output by removing unwanted characters.
    
    WHY CLEAN?
    OCR often produces:
    - Random special characters (!@#$%)
    - Extra spaces
    - Lowercase letters (plates are usually uppercase)
    
    We keep only letters, numbers, spaces, and hyphens.
    """
    # Keep only alphanumeric characters, spaces, and hyphens
    cleaned = re.sub(r'[^A-Za-z0-9\s\-]', '', raw_text)
    
    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())
    
    # Convert to uppercase (most plates use uppercase)
    cleaned = cleaned.upper()
    
    return cleaned


def read_plate_text(plate_image):
    """
    Use EasyOCR to read text from a cropped number plate image.
    
    HOW EasyOCR WORKS (simplified):
    1. It uses a pre-trained deep learning model internally
    2. The model was trained on millions of text images
    3. It detects text regions and recognizes characters
    4. It returns: [bounding_box, text, confidence_score]
    
    CONFIDENCE SCORE:
    - A number between 0 and 1
    - 0.9+ means very confident (probably correct)
    - 0.5-0.9 means somewhat confident (might have errors)
    - Below 0.5 means low confidence (likely wrong)
    
    Returns:
        text (str): The detected plate text (cleaned)
        confidence (float): Average confidence score
        raw_results (list): Raw EasyOCR output for debugging
    """
    if plate_image is None:
        print("[WARNING] No plate image provided for OCR.")
        return "", 0.0, []
    
    # Import EasyOCR here (it's slow to import, so we only do it when needed)
    try:
        import easyocr
    except ImportError:
        print("[ERROR] EasyOCR is not installed. Run: pip install easyocr")
        return "", 0.0, []
    
    # Preprocess the plate image for better OCR results
    processed_plate = preprocess_plate_for_ocr(plate_image)
    
    # Create an EasyOCR reader for English language
    # gpu=False means use CPU (simpler, works everywhere)
    # Set gpu=True if you have a CUDA-compatible GPU for faster processing
    print("[INFO] Initializing EasyOCR reader (this may take a moment on first run)...")
    reader = easyocr.Reader(['en'], gpu=False)
    
    # Run OCR on the preprocessed plate image
    # detail=1 returns bounding boxes + text + confidence
    print("[INFO] Running OCR on plate image...")
    results = reader.readtext(processed_plate, detail=1)
    
    if not results:
        print("[WARNING] OCR could not detect any text on the plate.")
        return "", 0.0, []
    
    # Combine all detected text pieces
    # (sometimes OCR splits the plate text into multiple parts)
    all_text = ""
    total_confidence = 0.0
    
    for (bbox, text, confidence) in results:
        all_text += text + " "
        total_confidence += confidence
        print(f"  [OCR] Detected: '{text}' (confidence: {confidence:.2f})")
    
    # Calculate average confidence
    avg_confidence = total_confidence / len(results)
    
    # Clean the combined text
    cleaned_text = clean_ocr_text(all_text)
    
    print(f"[INFO] Final plate text: '{cleaned_text}' (avg confidence: {avg_confidence:.2f})")
    
    return cleaned_text, avg_confidence, results


def draw_plate_text(image, text, confidence, plate_coords):
    """
    Draw the OCR result text on the output image.
    
    This puts the recognized plate number near the plate bounding box
    so the viewer can see what the system detected.
    """
    if plate_coords is None or text == "":
        return image
    
    annotated = image.copy()
    x, y, w, h = plate_coords
    
    # Create the label text
    label = f"Plate: {text} ({confidence:.0%})"
    
    # Draw a filled rectangle behind the text for readability
    (text_width, text_height), baseline = cv2.getTextSize(
        label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
    )
    cv2.rectangle(
        annotated,
        (x, y + h + 5),
        (x + text_width + 10, y + h + text_height + 15),
        (0, 255, 0),
        -1  # -1 means filled rectangle
    )
    
    # Draw the text in black on the green background
    cv2.putText(
        annotated,
        label,
        (x + 5, y + h + text_height + 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),    # Black text
        2
    )
    
    return annotated


# ============================================
# Test this module independently
# ============================================
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ocr.py <plate_image_path>")
        print("Example: python ocr.py sample_data/detected_plate.jpg")
    else:
        # Read the plate image
        plate_img = cv2.imread(sys.argv[1])
        if plate_img is not None:
            text, confidence, raw = read_plate_text(plate_img)
            print(f"\nResult: '{text}' with confidence {confidence:.2f}")
        else:
            print(f"Could not read image: {sys.argv[1]}")
