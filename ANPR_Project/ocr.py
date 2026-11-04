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
