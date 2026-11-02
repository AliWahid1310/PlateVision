"""
Unit tests for plate detector and candidate ranking.
"""
import numpy as np
import cv2
import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from plate_detector import calculate_candidate_score, crop_plate_safe

def test_candidate_scoring_valid_rect():
    image_shape = (600, 800)
    # 140x40 rectangle (aspect ratio = 3.5)
    pts = np.array([[[100, 100]], [[240, 100]], [[240, 140]], [[100, 140]]], dtype=np.int32)
    score = calculate_candidate_score(pts, image_shape)
    assert score > 0.5, f"Expected strong score for ideal plate, got {score}"

def test_crop_plate_safe_bounds():
    dummy = np.zeros((400, 600, 3), dtype=np.uint8)
    cropped, safe_bbox = crop_plate_safe(dummy, (5, 5, 50, 20), padding=10)
    assert cropped.shape[0] > 0 and cropped.shape[1] > 0
    assert safe_bbox[0] == 0
    assert safe_bbox[1] == 0

from plate_detector import order_corner_points, four_point_perspective_transform

def test_order_corner_points():
    unordered = np.array([[200, 200], [10, 10], [200, 10], [10, 200]], dtype="float32")
    ordered = order_corner_points(unordered)
    assert np.array_equal(ordered[0], [10, 10]) # Top-left
    assert np.array_equal(ordered[1], [200, 10]) # Top-right
    assert np.array_equal(ordered[2], [200, 200]) # Bottom-right
    assert np.array_equal(ordered[3], [10, 200]) # Bottom-left
