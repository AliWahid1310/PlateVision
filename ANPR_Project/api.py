"""
api.py — REST API serving ANPR, vehicle detection, audit history, and telemetry.
"""
import cv2
import numpy as np
import base64
import time
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import API_CFG
from logger import log_info, log_error
from preprocessing import resize_image, convert_to_grayscale, apply_gaussian_blur, auto_canny, apply_threshold, apply_clahe
from plate_detector import detect_plate, draw_plate_overlay
from ocr import read_plate_text, validate_plate_syntax
from vehicle_detector import load_yolo_model, detect_vehicles, draw_vehicle_boxes, get_optimal_device
from database import insert_scan_record, get_scan_records, get_detection_statistics
from schemas import ProcessResponse, HealthResponse, StatsResponse

yolo_model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global yolo_model
    log_info("API", "Loading YOLO neural model...")
    yolo_model = load_yolo_model()
    yield
    log_info("API", "Shutting down ANPR server...")

app = FastAPI(title="ANPR Vehicle Intelligence API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def image_to_base64(img):
    if img is None or img.size == 0:
        return None
    _, buf = cv2.imencode(".jpg", img)
    return base64.b64encode(buf).decode("utf-8")

@app.get("/api/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "yolo_loaded": yolo_model is not None,
        "easyocr_loaded": True,
        "device": get_optimal_device(),
        "version": "2.0.0"
    }
