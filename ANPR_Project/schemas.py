"""
schemas.py — Pydantic request and response models for FastAPI endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class VehicleItem(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: List[int]
    color: Optional[str] = "Unknown"

class ProcessingStepsBase64(BaseModel):
    gray: Optional[str] = None
    blurred: Optional[str] = None
    edges: Optional[str] = None
    threshold: Optional[str] = None
    plate_crop: Optional[str] = None

class ProcessResponse(BaseModel):
    status: str = "success"
    scan_id: Optional[int] = None
    plate_text: str = ""
    plate_confidence: float = 0.0
    plate_detected: bool = False
    plate_region: str = "Standard"
    vehicles: List[VehicleItem] = []
    vehicle_count: int = 0
    plate_image: Optional[str] = None
    annotated_image: Optional[str] = None
    processing_steps: ProcessingStepsBase64 = Field(default_factory=ProcessingStepsBase64)
    processing_time_ms: float = 0.0

class HealthResponse(BaseModel):
    status: str = "healthy"
    yolo_loaded: bool = False
    easyocr_loaded: bool = False
    device: str = "cpu"
    version: str = "2.0.0"

class StatsResponse(BaseModel):
    total_scans: int
    plates_detected: int
    detection_rate_pct: float
    avg_processing_time_ms: float
    fleet_distribution: Dict[str, int]
