"""
validators.py — Input validation and sanitization for image inputs.
"""
from typing import Tuple

class ImageValidationError(Exception):
    pass

def validate_image_dimensions(image, min_w=120, min_h=120, max_w=8000, max_h=8000):
    if image is None:
        raise ImageValidationError("Image buffer is empty or corrupted.")
    h, w = image.shape[:2]
    if w < min_w or h < min_h:
        raise ImageValidationError(f"Image too small: {w}x{h} (minimum {min_w}x{min_h}).")
    if w > max_w or h > max_h:
        raise ImageValidationError(f"Image dimensions exceed maximum allowed limits: {w}x{h}.")
    return True

def validate_aspect_ratio(w: int, h: int, min_ratio=0.2, max_ratio=5.0):
    if h == 0:
        return False
    ratio = w / float(h)
    return min_ratio <= ratio <= max_ratio
