"""
main.py — ANPR Project Entry Point
=====================================
This is the main file that ties everything together.
Run this file to process all images in the input_images/ folder.

USAGE:
    python main.py                    → Process all images in input_images/
    python main.py path/to/image.jpg  → Process a single image

WORKFLOW:
    1. Load the YOLO model (once, reused for all images)
    2. For each input image:
       a. Preprocess the image (grayscale, blur, edges)
       b. Detect the number plate using contours
       c. Run OCR on the cropped plate
       d. Detect vehicles using YOLO
       e. Combine all results onto one output image
       f. Save the output and print the summary
"""

import os
import sys
import cv2
import glob

# Import our custom modules
from preprocessing import preprocess_image
from plate_detector import detect_plate, save_plate
from ocr import read_plate_text, draw_plate_text
from vehicle_detector import load_yolo_model, detect_vehicles, draw_vehicle_boxes


# ============================================
# Configuration
# ============================================
INPUT_DIR = "input_images"
OUTPUT_DIR = "output_images"
SAMPLE_DIR = "sample_data"

# Supported image file extensions
IMAGE_EXTENSIONS = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]


def get_image_paths(input_dir):
    """
    Get all image file paths from the input directory.
    
    Returns a list of file paths, or an empty list if no images found.
    """
    image_paths = []
    
    for ext in IMAGE_EXTENSIONS:
        # glob.glob finds all files matching the pattern
        pattern = os.path.join(input_dir, ext)
        image_paths.extend(glob.glob(pattern))
    
    return sorted(image_paths)


def process_single_image(image_path, yolo_model, output_dir, sample_dir):
    """
    Process a single image through the complete ANPR pipeline.
    
    Steps:
    1. Preprocess the image
    2. Detect the number plate
    3. Run OCR on the plate
    4. Detect vehicles with YOLO
    5. Combine all annotations onto one output image
    6. Save the result and return the summary
    """
    print("=" * 60)
    print(f"Processing: {os.path.basename(image_path)}")
    print("=" * 60)
    
    # Get the base filename (without extension) for saving outputs
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # ------------------------------------------
    # STEP 1: Preprocess the image
    # ------------------------------------------
    print("\n--- Step 1: Preprocessing ---")
    preprocessed = preprocess_image(image_path, save_dir=output_dir)
    
    if preprocessed is None:
        print("[ERROR] Preprocessing failed. Skipping this image.\n")
        return None
    
    # Use the resized color image as our working image
    working_image = preprocessed["original"].copy()
    
    # ------------------------------------------
    # STEP 2: Detect the number plate
    # ------------------------------------------
    print("--- Step 2: Number Plate Detection ---")
    plate_image, plate_coords, annotated = detect_plate(
        preprocessed["original"],
        preprocessed["edges"]
    )
    
    # Save the cropped plate if found
    plate_text = ""
    plate_confidence = 0.0
    
    if plate_image is not None:
        plate_save_path = os.path.join(sample_dir, f"{base_name}_plate.jpg")
        save_plate(plate_image, plate_save_path)
        
        # ------------------------------------------
        # STEP 3: OCR on the plate
        # ------------------------------------------
        print("\n--- Step 3: OCR ---")
        plate_text, plate_confidence, raw_results = read_plate_text(plate_image)
        
        # Draw OCR text on the annotated image
        if plate_text:
            annotated = draw_plate_text(annotated, plate_text, plate_confidence, plate_coords)
    else:
        print("\n--- Step 3: OCR (Skipped — no plate detected) ---")
    
    # ------------------------------------------
    # STEP 4: Vehicle Detection with YOLO
    # ------------------------------------------
    print("\n--- Step 4: Vehicle Detection ---")
    vehicles = detect_vehicles(yolo_model, preprocessed["original"])
    
    # Draw vehicle boxes on the annotated image
    # (which already has the plate rectangle and OCR text)
    final_output = draw_vehicle_boxes(annotated, vehicles)
    
    # ------------------------------------------
    # STEP 5: Save the final output
    # ------------------------------------------
    output_path = os.path.join(output_dir, f"{base_name}_result.jpg")
    cv2.imwrite(output_path, final_output)
    print(f"\n[INFO] Final output saved: {output_path}")
    
    # ------------------------------------------
    # STEP 6: Print Summary
    # ------------------------------------------
    summary = {
        "image": os.path.basename(image_path),
        "vehicles": vehicles,
        "plate_text": plate_text,
        "plate_confidence": plate_confidence,
        "plate_detected": plate_image is not None,
        "output_path": output_path
    }
    
    return summary


def print_summary(summary):
    """
    Print a clean, readable summary of the results to the terminal.
    """
    print("\n" + "=" * 60)
    print("[RESULTS SUMMARY]")
    print("=" * 60)
    print(f"Image: {summary['image']}")
    print("-" * 40)
    
    # Vehicle results
    if summary["vehicles"]:
        print("\n[+] Vehicles Detected:")
        for i, v in enumerate(summary["vehicles"], 1):
            print(f"   {i}. {v['class_name']} (confidence: {v['confidence']:.0%})")
    else:
        print("\n[+] Vehicles Detected: None")
    
    # Plate results
    print()
    if summary["plate_detected"]:
        if summary["plate_text"]:
            print(f"[*] Number Plate: {summary['plate_text']}")
            print(f"[*] OCR Confidence: {summary['plate_confidence']:.0%}")
        else:
            print("[*] Number Plate: Detected but OCR could not read text")
    else:
        print("[*] Number Plate: Not detected")
    
    print(f"\n[+] Output saved: {summary['output_path']}")
    print("=" * 60)


def main():
    """
    Main function — orchestrates the entire ANPR pipeline.
    """
    # Ensure UTF-8 output encoding on Windows terminals if supported
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("AUTOMATIC NUMBER PLATE RECOGNITION (ANPR)")
    print("   & Basic Vehicle Detection System")
    print("=" * 60)
    
    # Check if a specific image path was provided as argument
    if len(sys.argv) > 1:
        image_paths = [sys.argv[1]]
        print(f"\nProcessing single image: {sys.argv[1]}")
    else:
        # Get all images from the input directory
        if not os.path.exists(INPUT_DIR):
            os.makedirs(INPUT_DIR, exist_ok=True)
            print(f"\n[INFO] Created '{INPUT_DIR}/' directory.")
            print(f"[INFO] Please put your vehicle images in '{INPUT_DIR}/' and run again.")
            return
        
        image_paths = get_image_paths(INPUT_DIR)
        
        if not image_paths:
            print(f"\n[WARNING] No images found in '{INPUT_DIR}/'")
            print(f"[INFO] Supported formats: {', '.join(IMAGE_EXTENSIONS)}")
            print(f"[INFO] Put your vehicle images in '{INPUT_DIR}/' and run again.")
            return
        
        print(f"\nFound {len(image_paths)} image(s) in '{INPUT_DIR}/'")
    
    # Create output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    
    # Load YOLO model once (reused for all images)
    print("\n--- Loading YOLO Model ---")
    yolo_model = load_yolo_model("yolov8n.pt")
    
    if yolo_model is None:
        print("[ERROR] Could not load YOLO model. Vehicle detection will be skipped.")
    
    # Process each image
    all_summaries = []
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"\n\n{'#' * 60}")
        print(f"  Image {i} of {len(image_paths)}")
        print(f"{'#' * 60}")
        
        summary = process_single_image(image_path, yolo_model, OUTPUT_DIR, SAMPLE_DIR)
        
        if summary:
            print_summary(summary)
            all_summaries.append(summary)
    
    # Final overview
    print("\n\n" + "=" * 60)
    print("[SUCCESS] PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total images processed: {len(all_summaries)}/{len(image_paths)}")
    print(f"Output directory: {OUTPUT_DIR}/")
    print(f"Cropped plates: {SAMPLE_DIR}/")
    print("=" * 60)


# ============================================
# Run the program
# ============================================
if __name__ == "__main__":
    main()
