"""
main.py - Unified CLI entry point for standalone ANPR processing.
"""
import os
import sys
import time
import argparse
import cv2
from logger import log_info, log_success, log_error, log_duration
from preprocessing import (
    read_image, resize_image, convert_to_grayscale,
    apply_clahe, apply_gaussian_blur, auto_canny, apply_threshold
)
from plate_detector import detect_plate, draw_plate_overlay
from ocr import read_plate_text, validate_plate_syntax
from vehicle_detector import load_yolo_model, detect_vehicles, draw_vehicle_boxes
from database import insert_scan_record
from datetime import datetime

OUTPUT_DIR = "output_images"
SAMPLE_DIR = "sample_data"

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SAMPLE_DIR, exist_ok=True)

def process_single_image(image_path, model=None, save_intermediates=True):
    """Full ANPR pipeline for a single image file."""
    ensure_dirs()
    basename = os.path.splitext(os.path.basename(image_path))[0]
    log_info("MAIN", f"Processing: {image_path}")
    start = time.perf_counter()

    raw = read_image(image_path)
    if raw is None:
        log_error("MAIN", f"Could not read image: {image_path}")
        return None

    resized = resize_image(raw)
    gray = convert_to_grayscale(resized)
    enhanced = apply_clahe(gray)
    blurred = apply_gaussian_blur(enhanced)
    edges = auto_canny(blurred)
    thresh = apply_threshold(enhanced)

    if save_intermediates:
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"{basename}_gray.jpg"), gray)
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"{basename}_blurred.jpg"), blurred)
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"{basename}_edges.jpg"), edges)
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"{basename}_thresh.jpg"), thresh)

    plate_crop, plate_bbox, approx = detect_plate(resized, edges)
    plate_text = ""
    plate_conf = 0.0
    plate_region = "Unknown"

    if plate_crop is not None:
        plate_text, plate_conf = read_plate_text(plate_crop)
        meta = validate_plate_syntax(plate_text)
        plate_region = meta["region"]
        cv2.imwrite(os.path.join(SAMPLE_DIR, f"{basename}_plate.jpg"), plate_crop)
        log_success("MAIN", f"Plate: {plate_text} (confidence: {plate_conf:.2f}, region: {plate_region})")
    else:
        log_error("MAIN", "No license plate detected.")

    vehicles = []
    if model is not None:
        vehicles = detect_vehicles(model, resized)
        log_info("MAIN", f"Detected {len(vehicles)} vehicle(s)")

    annotated = draw_vehicle_boxes(resized, vehicles)
    if plate_bbox is not None:
        annotated = draw_plate_overlay(annotated, plate_bbox, plate_text, plate_conf)
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"{basename}_result.jpg"), annotated)

    elapsed_ms = round((time.perf_counter() - start) * 1000.0, 1)
    log_info("MAIN", f"Pipeline completed in {elapsed_ms} ms")

    primary_v = vehicles[0] if vehicles else {}
    insert_scan_record({
        "timestamp": datetime.utcnow().isoformat(),
        "plate_text": plate_text,
        "plate_confidence": plate_conf,
        "plate_detected": plate_crop is not None,
        "plate_region": plate_region,
        "vehicle_class": primary_v.get("class_name", "Unknown"),
        "vehicle_confidence": primary_v.get("confidence", 0.0),
        "vehicle_color": primary_v.get("color", "Unknown"),
        "processing_time_ms": elapsed_ms,
        "image_name": os.path.basename(image_path)
    })

    return {
        "plate_text": plate_text,
        "plate_confidence": plate_conf,
        "plate_region": plate_region,
        "vehicles": vehicles,
        "elapsed_ms": elapsed_ms
    }

def main():
    parser = argparse.ArgumentParser(description="ANPR Vehicle Intelligence CLI")
    parser.add_argument("image", nargs="?", default="input_images/sample_car.jpg", help="Path to vehicle image")
    parser.add_argument("--no-yolo", action="store_true", help="Skip vehicle detection")
    parser.add_argument("--batch", nargs="*", help="Process multiple images")
    args = parser.parse_args()

    model = None
    if not args.no_yolo:
        with log_duration("YOLO Model Loading"):
            model = load_yolo_model()

    if args.batch:
        for img_path in args.batch:
            process_single_image(img_path, model)
    else:
        process_single_image(args.image, model)

if __name__ == "__main__":
    main()
