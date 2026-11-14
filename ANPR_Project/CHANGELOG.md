# Changelog

## [2.0.0] - 2026-11-14

### Added
- Centralized configuration system (`config.py`) with dataclass parameters
- CLAHE contrast enhancement and bilateral noise filtering
- Auto-Canny adaptive edge detection thresholds
- Morphological Blackhat and gradient operations
- Multi-criteria plate candidate scoring algorithm
- Perspective transformation for angled plate deskewing
- Fallback Sobel-based contour detection for low-contrast plates
- OCR character disambiguation (0/O, 8/B, 1/I)
- Pakistani provincial plate format validation (ICT, provincial)
- Multi-pass OCR with inverted binary fallback
- HSV-based dominant vehicle color classification
- CUDA/MPS/CPU auto-detection for YOLO inference
- SQLite audit database with search, pagination, and statistics
- CSV and JSON export endpoints
- Batch image processing CLI mode
- Fleet analytics dashboard with stats cards
- Detection history table with search and export
- Interactive image viewer with zoom controls
- Pydantic v2 response schemas
- Structured color logging with execution telemetry
- Comprehensive pytest test suite

### Changed
- Refactored preprocessing into modular pipeline functions
- Rebuilt plate detector with candidate scoring instead of first-match
- Enhanced OCR with multi-pass strategy and character correction
- Redesigned frontend with modern glass-card UI components
- Updated API with /health, /process, /history, /stats, /export endpoints

### Fixed
- Boundary clipping on tight crop coordinates
- OCR failures on inverted plate backgrounds
- Edge detection degradation under variable lighting
