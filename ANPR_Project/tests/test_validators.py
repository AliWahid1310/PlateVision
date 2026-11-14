"""
Tests for input validation module.
"""
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from validators import validate_image_dimensions, validate_aspect_ratio, ImageValidationError

def test_valid_image():
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    assert validate_image_dimensions(img) is True

def test_image_too_small():
    tiny = np.zeros((50, 50, 3), dtype=np.uint8)
    with pytest.raises(ImageValidationError):
        validate_image_dimensions(tiny)

def test_aspect_ratio_valid():
    assert validate_aspect_ratio(640, 480) is True

def test_aspect_ratio_extreme():
    assert validate_aspect_ratio(10, 1000) is False
