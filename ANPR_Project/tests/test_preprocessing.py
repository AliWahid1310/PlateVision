"""
Unit tests for image preprocessing module.
"""
import numpy as np
import cv2
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from preprocessing import (
    resize_image,
    convert_to_grayscale,
    apply_gaussian_blur,
    apply_clahe,
    auto_canny
)

def test_resize_image():
    dummy = np.zeros((600, 1200, 3), dtype=np.uint8)
    resized = resize_image(dummy, target_width=800)
    assert resized.shape[1] == 800
    assert resized.shape[0] == 400

def test_convert_to_grayscale():
    color = np.zeros((100, 100, 3), dtype=np.uint8)
    gray = convert_to_grayscale(color)
    assert len(gray.shape) == 2
    assert gray.shape == (100, 100)

def test_auto_canny():
    sample = np.zeros((100, 100), dtype=np.uint8)
    sample[30:70, 30:70] = 255
    edges = auto_canny(sample)
    assert edges is not None
    assert np.any(edges > 0)
