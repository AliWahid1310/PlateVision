"""
config.py — Centralized configuration parameters for the ANPR system.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

@dataclass
class PreprocessingConfig:
    target_width: int = 800
    gaussian_kernel: Tuple[int, int] = (5, 5)
    gaussian_sigma: float = 0
    bilateral_d: int = 11
    bilateral_sigma_color: int = 17
    bilateral_sigma_space: int = 17
    clahe_clip_limit: float = 2.0
    clahe_tile_grid: Tuple[int, int] = (8, 8)
    canny_sigma: float = 0.33

@dataclass
class PlateDetectorConfig:
    min_aspect_ratio: float = 1.8
    max_aspect_ratio: float = 6.5
    min_area_ratio: float = 0.005
    max_area_ratio: float = 0.18
    crop_padding_px: int = 8
    approx_epsilon_coeff: float = 0.02
    deskew_enabled: bool = True

@dataclass
class OCRConfig:
    languages: List[str] = field(default_factory=lambda: ["en"])
    min_confidence: float = 0.35
    fallback_confidence: float = 0.55
    target_plate_width: int = 320
    character_whitelist: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"

@dataclass
class VehicleDetectorConfig:
    model_name: str = "yolov8n.pt"
    confidence_threshold: float = 0.40
    vehicle_classes: Dict[int, str] = field(default_factory=lambda: {
        2: "Car",
        3: "Motorcycle",
        5: "Bus",
        7: "Truck"
    })
    vehicle_colors: Dict[int, Tuple[int, int, int]] = field(default_factory=lambda: {
        2: (255, 100, 0),
        3: (0, 165, 255),
        5: (0, 255, 255),
        7: (0, 0, 255)
    })

@dataclass
class DatabaseConfig:
    db_path: str = "anpr_audit.db"
    enable_wal_mode: bool = True

@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ])
    max_upload_size_mb: int = 15

# Global defaults
PREPROCESSING_CFG = PreprocessingConfig()
PLATE_CFG = PlateDetectorConfig()
OCR_CFG = OCRConfig()
VEHICLE_CFG = VehicleDetectorConfig()
DB_CFG = DatabaseConfig()
API_CFG = APIConfig()
