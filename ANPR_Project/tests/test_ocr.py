"""
Unit tests for OCR text cleaning and format matching.
"""
import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from ocr import clean_ocr_text, disambiguate_characters, validate_plate_syntax

def test_clean_ocr_text():
    raw = "  LE!A - 12#34  "
    cleaned = clean_ocr_text(raw)
    assert cleaned == "LEA - 1234"

def test_disambiguate_characters_digits():
    res = disambiguate_characters("78O1")
    assert "0" in res

def test_validate_plate_syntax_ict():
    meta = validate_plate_syntax("ICT 1234")
    assert meta["valid"] is True
    assert meta["region"] == "Islamabad Capital Territory"
