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
