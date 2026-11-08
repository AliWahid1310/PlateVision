"""
Tests for export utilities.
"""
import os
import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database import insert_scan_record
from export_utils import export_to_csv, export_to_json

def test_csv_export():
    insert_scan_record({"plate_text": "EXPORT-TEST", "plate_detected": True, "vehicle_class": "Car"})
    path = export_to_csv("exports/test_export.csv", limit=10)
    assert path is not None
    assert os.path.exists(path)

def test_json_export():
    path = export_to_json("exports/test_export.json", limit=10)
    assert path is not None
    assert os.path.exists(path)
