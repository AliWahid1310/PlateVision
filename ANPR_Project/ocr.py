"""
ocr.py — Optical Character Recognition module with multi-stage preprocessing.
"""
import cv2
import numpy as np
import re
from config import OCR_CFG
from logger import log_info, log_warn

_reader = None

def get_easyocr_reader():
    global _reader
    if _reader is None:
        try:
            import easyocr
            log_info("OCR", "Initializing EasyOCR Reader (English)...")
            _reader = easyocr.Reader(OCR_CFG.languages, gpu=False)
        except Exception as e:
            log_warn("OCR", f"Could not load EasyOCR: {e}")
            _reader = None
    return _reader

def preprocess_plate_for_ocr(plate_image):
    if plate_image is None or plate_image.size == 0:
        return None
    gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY) if len(plate_image.shape) == 3 else plate_image.copy()
    h, w = gray.shape[:2]
    if w < OCR_CFG.target_plate_width:
        scale = OCR_CFG.target_plate_width / float(w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    denoised = cv2.bilateralFilter(gray, 11, 17, 17)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def clean_ocr_text(raw_text: str) -> str:
    cleaned = re.sub(r'[^A-Za-z0-9\-\s]', '', raw_text)
    return ' '.join(cleaned.split()).upper()

def disambiguate_characters(text: str) -> str:
    """Corrects common OCR digit/letter confusion based on typical plate positional rules."""
    cleaned = clean_ocr_text(text)
    parts = cleaned.split()
    corrected_parts = []
    for p in parts:
        # If part is 2-4 chars and has digits mixed with letters at beginning, fix numbers to letters
        if len(p) <= 4 and re.search(r'[A-Za-z]', p):
            p = p.replace('0', 'O').replace('8', 'B').replace('1', 'I').replace('5', 'S')
        elif p.isdigit() or (len(p) >= 3 and any(c.isdigit() for c in p)):
            p = p.replace('O', '0').replace('D', '0').replace('B', '8').replace('I', '1').replace('Z', '2')
        corrected_parts.append(p)
    return ' '.join(corrected_parts)

def validate_plate_syntax(text: str):
    """Detects regional format (Pakistani provincial/federal standards or general alphanumeric)."""
    text_clean = re.sub(r'[^A-Z0-9]', '', text)
    if re.match(r'^(ICT|IDL)[0-9]{1,4}$', text_clean):
        return {"valid": True, "region": "Islamabad Capital Territory", "format": "ICT-XXXX"}
    if re.match(r'^[A-Z]{2,3}[0-9]{1,4}$', text_clean):
        return {"valid": True, "region": "Provincial Standard", "format": "ABC-XXXX"}
    if len(text_clean) >= 4:
        return {"valid": True, "region": "Standard Alphanumeric", "format": "General"}
    return {"valid": False, "region": "Unknown", "format": "Invalid"}
