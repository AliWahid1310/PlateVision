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
