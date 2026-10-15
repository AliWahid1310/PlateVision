"""
preprocessing.py — Core image preprocessing algorithms.
"""
import os
import cv2
import numpy as np
from config import PREPROCESSING_CFG
from logger import log_info, log_error

def read_image(image_path: str):
    if not os.path.exists(image_path):
        log_error("PREPROCESS", f"Image file not found: {image_path}")
        return None
    image = cv2.imread(image_path)
    if image is None:
        log_error("PREPROCESS", f"Could not decode image: {image_path}")
        return None
    h, w, c = image.shape
    log_info("PREPROCESS", f"Loaded image {os.path.basename(image_path)} ({w}x{h}, {c} channels)")
    return image

def resize_image(image, target_width: int = PREPROCESSING_CFG.target_width):
    if image is None:
        return None
    h, w = image.shape[:2]
    if w == target_width:
        return image.copy()
    aspect_ratio = h / float(w)
    target_height = int(target_width * aspect_ratio)
    resized = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA if w > target_width else cv2.INTER_CUBIC)
    log_info("PREPROCESS", f"Resized from {w}x{h} to {target_width}x{target_height}")
    return resized

def convert_to_grayscale(image):
    if image is None:
        return None
    if len(image.shape) == 2:
        return image.copy()
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def apply_gaussian_blur(gray_image, kernel_size=PREPROCESSING_CFG.gaussian_kernel, sigma=PREPROCESSING_CFG.gaussian_sigma):
    if gray_image is None:
        return None
    return cv2.GaussianBlur(gray_image, kernel_size, sigma)

def apply_edge_detection(blurred_image, low_threshold=50, high_threshold=150):
    if blurred_image is None:
        return None
    return cv2.Canny(blurred_image, low_threshold, high_threshold)

def apply_threshold(gray_image):
    if gray_image is None:
        return None
    _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def apply_clahe(gray_image, clip_limit=PREPROCESSING_CFG.clahe_clip_limit, tile_grid=PREPROCESSING_CFG.clahe_tile_grid):
    """Contrast Limited Adaptive Histogram Equalization for handling harsh sunlight and shadows."""
    if gray_image is None:
        return None
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid)
    return clahe.apply(gray_image)

def apply_bilateral_filter(image, d=PREPROCESSING_CFG.bilateral_d, sc=PREPROCESSING_CFG.bilateral_sigma_color, ss=PREPROCESSING_CFG.bilateral_sigma_space):
    """Bilateral filter to smooth flat textures while preserving sharp plate edge boundaries."""
    if image is None:
        return None
    return cv2.bilateralFilter(image, d, sc, ss)
