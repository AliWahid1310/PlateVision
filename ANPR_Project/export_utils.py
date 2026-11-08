"""
export_utils.py - Export scan results to CSV and JSON formats.
"""
import csv
import json
import os
from datetime import datetime
from database import get_scan_records
from logger import log_info, log_success

def export_to_csv(output_path="exports/scan_history.csv", limit=500):
    """Exports detection records to a CSV file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    records = get_scan_records(limit=limit)
    if not records:
        log_info("EXPORT", "No records to export.")
        return None
    fieldnames = list(records[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    log_success("EXPORT", f"Exported {len(records)} records to {output_path}")
    return output_path

def export_to_json(output_path="exports/scan_history.json", limit=500):
    """Exports detection records to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    records = get_scan_records(limit=limit)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"exported_at": datetime.utcnow().isoformat(), "records": records}, f, indent=2)
    log_success("EXPORT", f"Exported {len(records)} records to {output_path}")
    return output_path
