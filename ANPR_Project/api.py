"""
api.py — FastAPI Backend for ANPR Web Interface
==================================================
This module provides a REST API that wraps the existing ANPR pipeline,
allowing the Next.js frontend to upload images and receive detection results.

ENDPOINTS:
    POST /api/process  — Upload an image, run ANPR pipeline, return results
    GET  /api/health   — Health check endpoint

USAGE:
    python api.py
    # or
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
import io
import base64
import traceback
from contextlib import asynccontextmanager

import cv2
import numpy as np

# FastAPI imports
try:
    from fastapi import FastAPI, File, UploadFile, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
except ImportError:
    print("[ERROR] FastAPI is not installed. Run: pip install fastapi uvicorn python-multipart")
    sys.exit(1)

# Import our existing ANPR modules
from preprocessing import preprocess_image, read_image, resize_image, convert_to_grayscale, apply_gaussian_blur, apply_edge_detection, apply_threshold
from plate_detector import detect_plate, save_plate
from ocr import read_plate_text
from vehicle_detector import load_yolo_model, detect_vehicles, draw_vehicle_boxes


# ============================================
# Global state — YOLO model loaded once
# ============================================
yolo_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the YOLO model once at startup."""
    global yolo_model
    print("[API] Loading YOLO model at startup...")
    yolo_model = load_yolo_model("yolov8n.pt")
    if yolo_model is None:
        print("[API] WARNING: YOLO model could not be loaded. Vehicle detection will be unavailable.")
    else:
        print("[API] YOLO model loaded successfully!")
    yield
    print("[API] Shutting down...")


# ============================================
# Create FastAPI app
# ============================================
app = FastAPI(
    title="ANPR API",
    description="Automatic Number Plate Recognition & Vehicle Detection API",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS so the Next.js frontend (localhost:3000) can call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Helper functions
# ============================================
def image_to_base64(image, format=".jpg"):
    """Convert an OpenCV image (numpy array) to a base64-encoded string."""
    if image is None:
        return None
    success, buffer = cv2.imencode(format, image)
    if not success:
        return None
    return base64.b64encode(buffer).decode("utf-8")


def decode_upload_image(file_bytes):
    """Decode uploaded file bytes into an OpenCV image."""
    nparr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


# ============================================
# API Endpoints
# ============================================
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "yolo_loaded": yolo_model is not None,
    }


@app.post("/api/process")
async def process_image(file: UploadFile = File(...)):
    """
    Process an uploaded image through the complete ANPR pipeline.
    
    Returns JSON with:
    - vehicles: List of detected vehicles (type, confidence, bbox)
    - plate_text: Detected plate text
    - plate_confidence: OCR confidence score
    - plate_detected: Whether a plate was found
    - output_image: Base64-encoded annotated image
    - plate_image: Base64-encoded cropped plate image
    - processing_steps: Base64-encoded intermediate images
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (jpg, png, etc.)")
    
    try:
        # Read the uploaded file
        file_bytes = await file.read()
        original = decode_upload_image(file_bytes)
        
        if original is None:
            raise HTTPException(status_code=400, detail="Could not decode the uploaded image.")
        
        print(f"\n[API] Processing image: {file.filename} ({original.shape})")
        
        # ------------------------------------------
        # STEP 1: Preprocessing
        # ------------------------------------------
        resized = resize_image(original)
        gray = convert_to_grayscale(resized)
        blurred = apply_gaussian_blur(gray)
        edges = apply_edge_detection(blurred)
        thresh = apply_threshold(gray)
        
        processing_steps = {
            "original": image_to_base64(resized),
            "grayscale": image_to_base64(gray),
            "blurred": image_to_base64(blurred),
            "edges": image_to_base64(edges),
            "threshold": image_to_base64(thresh),
        }
        
        # ------------------------------------------
        # STEP 2: Plate Detection
        # ------------------------------------------
        plate_image, plate_coords, annotated = detect_plate(resized, edges)
        
        plate_text = ""
        plate_confidence = 0.0
        
        if plate_image is not None:
            # ------------------------------------------
            # STEP 3: OCR
            # ------------------------------------------
            plate_text, plate_confidence, raw_results = read_plate_text(plate_image)
            
            # Draw OCR text on annotated image
            if plate_text:
                from ocr import draw_plate_text
                annotated = draw_plate_text(annotated, plate_text, plate_confidence, plate_coords)
        
        # ------------------------------------------
        # STEP 4: Vehicle Detection
        # ------------------------------------------
        vehicles_list = []
        if yolo_model is not None:
            vehicles = detect_vehicles(yolo_model, resized)
            final_output = draw_vehicle_boxes(annotated, vehicles)
            
            for v in vehicles:
                vehicles_list.append({
                    "class_id": v["class_id"],
                    "class_name": v["class_name"],
                    "confidence": round(v["confidence"], 4),
                    "bbox": list(v["bbox"]),
                })
        else:
            final_output = annotated
        
        # ------------------------------------------
        # Build response
        # ------------------------------------------
        response = {
            "success": True,
            "filename": file.filename,
            "image_size": {"width": resized.shape[1], "height": resized.shape[0]},
            "vehicles": vehicles_list,
            "vehicle_count": len(vehicles_list),
            "plate_text": plate_text,
            "plate_confidence": round(plate_confidence, 4),
            "plate_detected": plate_image is not None,
            "output_image": image_to_base64(final_output),
            "plate_image": image_to_base64(plate_image),
            "processing_steps": processing_steps,
        }
        
        print(f"[API] Done! Vehicles: {len(vehicles_list)}, Plate: '{plate_text}'")
        return JSONResponse(content=response)
    
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# ============================================
# Run the server
# ============================================
if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  ANPR API Server")
    print("  http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
