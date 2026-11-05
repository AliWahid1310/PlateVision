"""
vehicle_detector.py — YOLOv8 vehicle detection and dominant HSV color classification.
"""
import cv2
import numpy as np
from config import VEHICLE_CFG
from logger import log_info, log_warn

COLOR_RANGES = [
    ("White", np.array([0, 0, 180]), np.array([180, 40, 255])),
    ("Black", np.array([0, 0, 0]), np.array([180, 255, 50])),
    ("Silver / Gray", np.array([0, 0, 50]), np.array([180, 45, 180])),
    ("Red", np.array([0, 100, 70]), np.array([10, 255, 255])),
    ("Red", np.array([170, 100, 70]), np.array([180, 255, 255])),
    ("Blue", np.array([100, 100, 50]), np.array([130, 255, 255])),
    ("Yellow", np.array([20, 100, 100]), np.array([35, 255, 255])),
    ("Green", np.array([36, 100, 50]), np.array([85, 255, 255]))
]

def classify_vehicle_color(image, bbox):
    """Extracts dominant color from central region of detected vehicle box in HSV space."""
    x1, y1, x2, y2 = bbox
    crop = image[y1:y2, x1:x2]
    if crop.size == 0:
        return "Unknown"
    h, w = crop.shape[:2]
    center_crop = crop[int(h*0.25):int(h*0.75), int(w*0.2):int(w*0.8)]
    if center_crop.size == 0:
        return "Unknown"
    
    hsv = cv2.cvtColor(center_crop, cv2.COLOR_BGR2HSV)
    max_score = 0
    detected_color = "Silver / Gray"
    for name, lower, upper in COLOR_RANGES:
        mask = cv2.inRange(hsv, lower, upper)
        score = np.count_nonzero(mask)
        if score > max_score:
            max_score = score
            detected_color = name
    return detected_color

def get_optimal_device():
    try:
        import torch
        if torch.cuda.is_available():
            log_info("VEHICLE_DETECTOR", f"CUDA GPU available: {torch.cuda.get_device_name(0)}")
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"

def load_yolo_model(model_name=VEHICLE_CFG.model_name):
    try:
        from ultralytics import YOLO
        device = get_optimal_device()
        log_info("VEHICLE_DETECTOR", f"Loading YOLO model {model_name} on device '{device}'...")
        model = YOLO(model_name)
        return model
    except Exception as e:
        log_warn("VEHICLE_DETECTOR", f"Could not load YOLO model: {e}")
        return None

def draw_vehicle_boxes(image, vehicles):
    """Renders sleek bounding boxes with vehicle classification, confidence, and color badges."""
    annotated = image.copy()
    for v in vehicles:
        x1, y1, x2, y2 = v["bbox"]
        class_id = v.get("class_id", 2)
        color = VEHICLE_CFG.vehicle_colors.get(class_id, (255, 100, 0))
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        label = f"{v['class_name']} ({v['confidence']*100:.0f}%)"
        if v.get("color"):
            label += f" | {v['color']}"
            
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        badge_y = max(th + 6, y1)
        cv2.rectangle(annotated, (x1, badge_y - th - 6), (x1 + tw + 8, badge_y + baseline), (20, 24, 33), -1)
        cv2.putText(annotated, label, (x1 + 4, badge_y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
    return annotated
