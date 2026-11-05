"""
Unit tests for vehicle detection and color classifier.
"""
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from vehicle_detector import classify_vehicle_color

def test_classify_vehicle_color_white():
    white_car = np.full((100, 100, 3), 255, dtype=np.uint8)
    color = classify_vehicle_color(white_car, (0, 0, 100, 100))
    assert color == "White"

def test_classify_vehicle_color_black():
    black_car = np.zeros((100, 100, 3), dtype=np.uint8)
    color = classify_vehicle_color(black_car, (0, 0, 100, 100))
    assert color == "Black"
