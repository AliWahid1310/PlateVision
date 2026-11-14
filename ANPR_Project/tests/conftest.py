"""
conftest.py - Shared pytest fixtures for the ANPR test suite.
"""
import pytest
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture
def sample_color_image():
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

@pytest.fixture
def sample_gray_image():
    return np.random.randint(0, 255, (480, 640), dtype=np.uint8)

@pytest.fixture
def sample_plate_crop():
    plate = np.full((60, 200, 3), 220, dtype=np.uint8)
    return plate
