# ANPR Audit Database Schema

## Table: `scans`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Auto-increment unique scan index |
| `timestamp` | TEXT | ISO-8601 UTC timestamp |
| `plate_text` | TEXT | Recognized plate string |
| `plate_confidence` | REAL | OCR confidence score [0.0 - 1.0] |
| `plate_detected` | INTEGER | 1 if plate isolated, 0 otherwise |
| `plate_region` | TEXT | Region (e.g. Islamabad, Provincial) |
| `vehicle_class` | TEXT | COCO class name (Car, Bus, etc.) |
| `vehicle_confidence`| REAL | YOLO detection score |
| `vehicle_color` | TEXT | Dominant vehicle body color |
| `processing_time_ms`| REAL | Full pipeline turnaround time |
