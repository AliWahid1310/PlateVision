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

@app.post("/api/process", response_model=ProcessResponse)
async def process_image_endpoint(file: UploadFile = File(...)):
    start_time = time.perf_counter()
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    raw = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if raw is None:
        raise HTTPException(status_code=400, detail="Invalid or unsupported image file.")
    
    resized = resize_image(raw)
    gray = convert_to_grayscale(resized)
    clahe = apply_clahe(gray)
    blurred = apply_gaussian_blur(clahe)
    edges = auto_canny(blurred)
    thresh = apply_threshold(clahe)
    
    plate_crop, plate_bbox, approx = detect_plate(resized, edges)
    plate_detected = plate_crop is not None
    plate_text = ""
    plate_conf = 0.0
    plate_region = "Standard"
    
    if plate_detected:
        plate_text, plate_conf = read_plate_text(plate_crop)
        meta = validate_plate_syntax(plate_text)
        plate_region = meta["region"]

    vehicles = detect_vehicles(yolo_model, resized) if yolo_model else []
    annotated = draw_vehicle_boxes(resized, vehicles)
    if plate_detected:
        annotated = draw_plate_overlay(annotated, plate_bbox, plate_text, plate_conf)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 1)

    primary_v = vehicles[0] if vehicles else {}
    record_id = insert_scan_record({
        "timestamp": datetime.utcnow().isoformat(),
        "plate_text": plate_text,
        "plate_confidence": plate_conf,
        "plate_detected": plate_detected,
        "plate_region": plate_region,
        "vehicle_class": primary_v.get("class_name", "Car"),
        "vehicle_confidence": primary_v.get("confidence", 0.0),
        "vehicle_color": primary_v.get("color", "Unknown"),
        "processing_time_ms": elapsed_ms,
        "image_name": file.filename
    })

    return {
        "status": "success",
        "scan_id": record_id,
        "plate_text": plate_text,
        "plate_confidence": plate_conf,
        "plate_detected": plate_detected,
        "plate_region": plate_region,
        "vehicles": vehicles,
        "vehicle_count": len(vehicles),
        "plate_image": image_to_base64(plate_crop),
        "annotated_image": image_to_base64(annotated),
        "processing_steps": {
            "gray": image_to_base64(gray),
            "blurred": image_to_base64(blurred),
            "edges": image_to_base64(edges),
            "threshold": image_to_base64(thresh)
        },
        "processing_time_ms": elapsed_ms
    }

@app.get("/api/history")
def get_history_endpoint(limit: int = 50, offset: int = 0, search: str = ""):
    records = get_scan_records(limit=limit, offset=offset, search=search)
    return {"records": records, "count": len(records)}

@app.get("/api/stats", response_model=StatsResponse)
def get_stats_endpoint():
    return get_detection_statistics()

@app.middleware("http")
async def add_timing_headers(request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - t0) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{elapsed:.2f}"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host=API_CFG.host, port=API_CFG.port, reload=True)
