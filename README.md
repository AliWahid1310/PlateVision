# ANPR Vehicle Intelligence System

A full-stack computer vision solution for Automatic Number Plate Recognition (ANPR) and vehicle fleet analysis.

## Features
- **License Plate Detection** using OpenCV contour analysis with perspective correction
- **OCR Engine** powered by EasyOCR with multi-pass and character disambiguation
- **Vehicle Detection** using YOLOv8 with dominant color classification
- **Audit Database** with SQLite for detection history and fleet statistics
- **Web Dashboard** built with Next.js 16 featuring real-time analytics

## Quick Start

### Backend
```bash
cd ANPR_Project
pip install -r requirements.txt
python api.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### CLI Mode
```bash
cd ANPR_Project
python main.py input_images/sample_car.jpg
python main.py --batch img1.jpg img2.jpg img3.jpg
```

## Architecture
```
ANPR_Project/          # Python backend
  config.py            # Centralized parameters
  preprocessing.py     # Image pipeline (CLAHE, Auto-Canny, bilateral)
  plate_detector.py    # Contour scoring and perspective deskew
  ocr.py               # Multi-pass OCR with disambiguation
  vehicle_detector.py  # YOLOv8 + HSV color classification
  database.py          # SQLite audit persistence
  api.py               # FastAPI REST server
  schemas.py           # Pydantic response models
  tests/               # pytest suite

frontend/              # Next.js 16 dashboard
  app/                 # App Router pages
  components/          # React UI components
```

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | System health and device info |
| POST | `/api/process` | Upload image, run ANPR pipeline |
| GET | `/api/history` | Paginated detection log |
| GET | `/api/stats` | Fleet analytics summary |
| GET | `/api/export/csv` | Download detection history as CSV |
| GET | `/api/export/json` | Download detection history as JSON |

## License
MIT - see [LICENSE](LICENSE)
