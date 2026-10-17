"""
plate_detector.py — License plate contour extraction and candidate scoring.
"""
import cv2
import numpy as np
from config import PLATE_CFG
from logger import log_info, log_warn

def find_contours(edge_image):
    contours, _ = cv2.findContours(
        edge_image.copy(),
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:35]
    log_info("PLATE_DETECTOR", f"Evaluated top {len(sorted_contours)} contours by area.")
    return sorted_contours

def calculate_candidate_score(approx, image_shape):
    """Calculates geometric fitness score for a candidate plate contour (0.0 to 1.0)."""
    if len(approx) != 4:
        return 0.0
    x, y, w, h = cv2.boundingRect(approx)
    if h == 0:
        return 0.0
    aspect_ratio = w / float(h)
    if not (PLATE_CFG.min_aspect_ratio <= aspect_ratio <= PLATE_CFG.max_aspect_ratio):
        return 0.0
    
    area = cv2.contourArea(approx)
    img_area = image_shape[0] * image_shape[1]
    area_ratio = area / float(img_area)
    if not (PLATE_CFG.min_area_ratio <= area_ratio <= PLATE_CFG.max_area_ratio):
        return 0.0

    rect_area = w * h
    solidity = area / float(rect_area) if rect_area > 0 else 0
    aspect_ideal = 3.5
    aspect_score = 1.0 - min(abs(aspect_ratio - aspect_ideal) / 3.0, 1.0)
    solidity_score = min(solidity / 0.85, 1.0)
    
    return float((aspect_score * 0.6) + (solidity_score * 0.4))
