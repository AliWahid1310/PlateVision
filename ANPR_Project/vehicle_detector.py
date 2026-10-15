"""
vehicle_detector.py — Vehicle Detection Module
=================================================
This module uses a pretrained YOLOv8 nano model to detect vehicles.

WHAT IS YOLO?
YOLO (You Only Look Once) is an object detection algorithm.
- It looks at an image ONCE and detects all objects in it
- It draws bounding boxes around each detected object
- It tells you WHAT the object is (car, bus, etc.) and HOW confident it is

WHY YOLOv8 NANO?
- "Nano" is the smallest and fastest version (~6 MB)
- It's pretrained on the COCO dataset (80 common object classes)
- No training needed — just load and use
- Good enough for a prototype/internship project
- The 'ultralytics' library makes it very easy to use

COCO VEHICLE CLASSES:
The COCO dataset includes these vehicle-related classes:
- car (class ID: 2)
- motorcycle (class ID: 3)
- bus (class ID: 5)
- truck (class ID: 7)
"""

import cv2
import numpy as np


# Vehicle class IDs in the COCO dataset
# COCO has 80 classes; these are the ones relevant to vehicles
VEHICLE_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

# Colors for drawing bounding boxes (BGR format)
# Each vehicle type gets a different color for easy distinction
VEHICLE_COLORS = {
    2: (255, 100, 0),     # Blue-ish for Car
    3: (0, 165, 255),     # Orange for Motorcycle
    5: (0, 255, 255),     # Yellow for Bus
    7: (0, 0, 255),       # Red for Truck
}


def load_yolo_model(model_name="yolov8n.pt"):
    """
    Load the pretrained YOLOv8 model.
    
    On first run, ultralytics will automatically download the model file.
    After that, it's cached locally so it won't download again.
    
    model_name options:
    - 'yolov8n.pt' → Nano (fastest, smallest, ~6 MB)
    - 'yolov8s.pt' → Small (more accurate, ~22 MB)
    - 'yolov8m.pt' → Medium (even more accurate, ~50 MB)
    
    We use Nano for simplicity and speed.
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] ultralytics is not installed. Run: pip install ultralytics")
        return None
    
    print(f"[INFO] Loading YOLO model: {model_name}")
    model = YOLO(model_name)
    print("[INFO] YOLO model loaded successfully!")
    return model


def detect_vehicles(model, image, confidence_threshold=0.4):
    """
    Detect vehicles in an image using the YOLO model.
    
    HOW DETECTION WORKS:
    1. The image is passed through the YOLO neural network
    2. YOLO outputs a list of detections, each with:
       - Bounding box coordinates (x1, y1, x2, y2)
       - Class ID (what type of object)
       - Confidence score (how sure the model is)
    3. We filter to keep only vehicle classes (car, motorcycle, bus, truck)
    4. We filter by confidence threshold (ignore low-confidence detections)
    
    Parameters:
        model: The loaded YOLO model
        image: The input image (numpy array)
        confidence_threshold: Minimum confidence to accept (0.0 to 1.0)
    
    Returns:
        vehicles: List of dictionaries, each containing:
            - 'class_id': COCO class ID
            - 'class_name': Human-readable name (e.g., "Car")
            - 'confidence': Detection confidence (0.0 to 1.0)
            - 'bbox': (x1, y1, x2, y2) bounding box coordinates
    """
    if model is None:
        print("[ERROR] YOLO model is not loaded.")
        return []
    
    # Run YOLO inference
    # verbose=False suppresses the default YOLO output
    print("[INFO] Running vehicle detection...")
    results = model(image, verbose=False)
    
    vehicles = []
    
    # Process each detection
    # results[0] contains all detections for the first (and only) image
    for result in results:
        boxes = result.boxes  # All detected bounding boxes
        
        for box in boxes:
            # Get the class ID and confidence
            class_id = int(box.cls[0])          # What object is it?
            confidence = float(box.conf[0])      # How confident?
            
            # Only keep vehicle classes with sufficient confidence
            if class_id in VEHICLE_CLASSES and confidence >= confidence_threshold:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()  # Convert tensor to list
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                vehicle_info = {
                    "class_id": class_id,
                    "class_name": VEHICLE_CLASSES[class_id],
                    "confidence": confidence,
                    "bbox": (x1, y1, x2, y2)
                }
                vehicles.append(vehicle_info)
                
                print(f"  [YOLO] Detected: {vehicle_info['class_name']} "
                      f"(confidence: {confidence:.2f})")
    
    if not vehicles:
        print("[WARNING] No vehicles detected in this image.")
    else:
        print(f"[INFO] Total vehicles detected: {len(vehicles)}")
    
    return vehicles


def draw_vehicle_boxes(image, vehicles):
    """
    Draw bounding boxes and labels around detected vehicles.
    
    For each vehicle:
    - Draw a colored rectangle around it
    - Add a label showing the vehicle type and confidence
    - Use different colors for different vehicle types
    """
    annotated = image.copy()
    
    for vehicle in vehicles:
        x1, y1, x2, y2 = vehicle["bbox"]
        class_id = vehicle["class_id"]
        class_name = vehicle["class_name"]
        confidence = vehicle["confidence"]
        
        # Get the color for this vehicle type
        color = VEHICLE_COLORS.get(class_id, (255, 255, 255))
        
        # Draw the bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        # Create the label text
        label = f"{class_name}: {confidence:.0%}"
        
        # Calculate text size for the background rectangle
        (text_w, text_h), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        
        # Draw filled rectangle behind text for readability
        cv2.rectangle(
            annotated,
            (x1, y1 - text_h - 10),
            (x1 + text_w + 10, y1),
            color,
            -1  # Filled
        )
        
        # Draw the label text
        cv2.putText(
            annotated,
            label,
            (x1 + 5, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),  # Black text on colored background
            2
        )
    
    return annotated


# ============================================
# Test this module independently
# ============================================
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vehicle_detector.py <image_path>")
        print("Example: python vehicle_detector.py input_images/car1.jpg")
    else:
        # Load model
        model = load_yolo_model()
        
        # Read image
        image = cv2.imread(sys.argv[1])
        if image is None:
            print(f"Could not read image: {sys.argv[1]}")
        else:
            # Detect vehicles
            vehicles = detect_vehicles(model, image)
            
            # Draw boxes
            output = draw_vehicle_boxes(image, vehicles)
            
            # Save result
            cv2.imwrite("output_images/vehicle_detection_result.jpg", output)
            print("\nVehicle detection complete! Check output_images/ folder.")
