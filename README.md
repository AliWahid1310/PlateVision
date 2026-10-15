# 🚗 Automatic Number Plate Recognition (ANPR) & Vehicle Intelligence System

A full-stack, production-ready computer vision solution combining OpenCV, YOLOv8 object detection, EasyOCR, and a Next.js 16 reactive frontend.

## 🌟 Core Highlights
- **Multi-stage Image Preprocessing**: CLAHE contrast balance, auto-Canny gradient thresholds, bilateral edge-preserving smoothing.
- **Robust Plate Detection**: 4-point contour extraction, perspective deskewing transformation, and geometric candidate scoring.
- **Enhanced OCR Engine**: Multi-pass character recognition, OCR character disambiguation (e.g. 0/O, 8/B), and pattern heuristics.
- **Vehicle Classification & Color Tracking**: YOLOv8 deep inference coupled with HSV dominant color extraction.
- **Audit Logging**: SQLite database recording scans, bounding boxes, latencies, and vehicle analytics.
- **Next.js Web Client**: Live camera capture, interactive zoom & pan, detection history table, and fleet statistics dashboard.

## 📐 Architecture Pipeline
```
[Vehicle Image] ──> [Resize & CLAHE] ──> [Bilateral Filter] ──> [Auto-Canny Edges]
                                                                      │
     ┌────────────────────────────────────────────────────────────────┘
     ▼
[Contour Geometry & Aspect Ratio] ──> [Perspective Warp / Deskew] ──> [Cropped Plate]
                                                                            │
     ┌──────────────────────────────────────────────────────────────────────┘
     ▼
[Binarization & Inversion] ──> [EasyOCR Inference] ──> [Alphanumeric Disambiguation] ──> Final Plate Text
                                                                                                 │
[Full Image] ──> [YOLOv8 Detection] ──> [HSV Color Clustering] ──> Vehicle Specs ───────────────┼──> [SQLite / Next.js Dashboard]
```
