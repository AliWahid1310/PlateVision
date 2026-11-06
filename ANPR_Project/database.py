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
