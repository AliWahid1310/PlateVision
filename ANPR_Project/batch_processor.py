"""
batch_processor.py - Bulk image processing with progress tracking.
"""
import os
import glob
from logger import log_info, log_success

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

def discover_images(directory):
    """Scans a directory and returns list of supported image file paths."""
    found = []
    for ext in SUPPORTED_EXTENSIONS:
        found.extend(glob.glob(os.path.join(directory, f"*{ext}")))
        found.extend(glob.glob(os.path.join(directory, f"*{ext.upper()}")))
    unique = sorted(set(found))
    log_info("BATCH", f"Discovered {len(unique)} images in {directory}")
    return unique

def generate_batch_report(results):
    """Generates a summary report from batch processing results."""
    total = len(results)
    detected = sum(1 for r in results if r and r.get("plate_text"))
    avg_time = sum(r.get("elapsed_ms", 0) for r in results if r) / max(total, 1)
    vehicle_counts = {}
    for r in results:
        if r and r.get("vehicles"):
            for v in r["vehicles"]:
                name = v.get("class_name", "Unknown")
                vehicle_counts[name] = vehicle_counts.get(name, 0) + 1
    return {
        "total_images": total,
        "plates_detected": detected,
        "detection_rate": round(detected / max(total, 1) * 100, 1),
        "avg_processing_ms": round(avg_time, 1),
        "vehicle_summary": vehicle_counts
    }
