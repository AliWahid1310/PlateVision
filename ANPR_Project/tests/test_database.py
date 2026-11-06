"""
Unit tests for database audit layer.
"""
import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from database import insert_scan_record, get_scan_records, get_detection_statistics

def test_database_insert_and_retrieve():
    rec_id = insert_scan_record({
        "plate_text": "TEST-1234",
        "plate_detected": True,
        "vehicle_class": "Car",
        "processing_time_ms": 42.5
    })
    assert rec_id > 0
    records = get_scan_records(limit=5, search="TEST-1234")
    assert len(records) > 0
    assert records[0]["plate_text"] == "TEST-1234"

def test_database_statistics():
    stats = get_detection_statistics()
    assert "total_scans" in stats
    assert "detection_rate_pct" in stats
