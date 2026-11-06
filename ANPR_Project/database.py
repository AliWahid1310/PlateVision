"""
database.py — SQLite audit logging and telemetry persistence.
"""
import sqlite3
import os
import json
from datetime import datetime
from config import DB_CFG
from logger import log_info

def get_db_connection():
    conn = sqlite3.connect(DB_CFG.db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        plate_text TEXT,
        plate_confidence REAL,
        plate_detected INTEGER,
        plate_region TEXT,
        vehicle_class TEXT,
        vehicle_confidence REAL,
        vehicle_color TEXT,
        processing_time_ms REAL,
        image_name TEXT
    );
    """)
    conn.commit()
    conn.close()
    log_info("DATABASE", "Initialized SQLite audit database schema.")

init_database()

def insert_scan_record(data: dict) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO scans (
        timestamp, plate_text, plate_confidence, plate_detected,
        plate_region, vehicle_class, vehicle_confidence,
        vehicle_color, processing_time_ms, image_name
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("timestamp", datetime.utcnow().isoformat()),
        data.get("plate_text", ""),
        data.get("plate_confidence", 0.0),
        1 if data.get("plate_detected") else 0,
        data.get("plate_region", "Standard"),
        data.get("vehicle_class", "Car"),
        data.get("vehicle_confidence", 0.0),
        data.get("vehicle_color", "Unknown"),
        data.get("processing_time_ms", 0.0),
        data.get("image_name", "upload.jpg")
    ))
    record_id = cur.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_scan_records(limit=50, offset=0, search=""):
    conn = get_db_connection()
    cur = conn.cursor()
    if search:
        query = "SELECT * FROM scans WHERE plate_text LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?"
        rows = cur.execute(query, (f"%{search}%", limit, offset)).fetchall()
    else:
        query = "SELECT * FROM scans ORDER BY id DESC LIMIT ? OFFSET ?"
        rows = cur.execute(query, (limit, offset)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_detection_statistics():
    conn = get_db_connection()
    cur = conn.cursor()
    total_scans = cur.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
    plates_detected = cur.execute("SELECT COUNT(*) FROM scans WHERE plate_detected = 1").fetchone()[0]
    avg_latency = cur.execute("SELECT AVG(processing_time_ms) FROM scans").fetchone()[0] or 0.0
    
    fleet_rows = cur.execute("SELECT vehicle_class, COUNT(*) as cnt FROM scans GROUP BY vehicle_class").fetchall()
    fleet_distribution = {r["vehicle_class"]: r["cnt"] for r in fleet_rows}
    
    conn.close()
    detection_rate = (plates_detected / total_scans * 100.0) if total_scans > 0 else 0.0
    return {
        "total_scans": total_scans,
        "plates_detected": plates_detected,
        "detection_rate_pct": round(detection_rate, 1),
        "avg_processing_time_ms": round(avg_latency, 1),
        "fleet_distribution": fleet_distribution
    }

def add_database_indices():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_scans_timestamp ON scans(timestamp);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_scans_plate ON scans(plate_text);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_scans_vehicle ON scans(vehicle_class);")
    conn.commit()
    conn.close()

add_database_indices()
