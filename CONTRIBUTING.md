# Contributing to ANPR Vehicle Intelligence System

## Development Setup
1. Clone this repository
2. Install Python dependencies: `pip install -r ANPR_Project/requirements.txt`
3. Install frontend dependencies: `cd frontend && npm install`
4. Start the backend: `cd ANPR_Project && python api.py`
5. Start the frontend: `cd frontend && npm run dev`

## Project Structure
- `ANPR_Project/` - Python backend (FastAPI, OpenCV, YOLOv8, EasyOCR)
- `frontend/` - Next.js web dashboard
- `ANPR_Project/tests/` - pytest test suite

## Code Style
- Python: Follow PEP 8 with type hints
- JavaScript: Follow ESLint + Next.js conventions
- Commit messages: Use conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`)

## Running Tests
```bash
cd ANPR_Project
pytest tests/ -v
```
