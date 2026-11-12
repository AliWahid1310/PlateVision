# ANPR Vehicle Intelligence - Web Dashboard

## Tech Stack
- **Next.js 16** with App Router
- **React 19** with hooks
- **Lucide Icons** for UI iconography
- **CSS Variables** for theming

## Features
- Drag-and-drop image upload with preview
- Real-time ANPR pipeline visualization (grayscale, edges, threshold)
- Interactive image viewer with zoom controls
- Vehicle detection with color classification
- Fleet analytics dashboard with statistics
- Searchable detection history table
- CSV and JSON export

## Development
```bash
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000).

## Backend Connection
The frontend expects the Python FastAPI server running on port 8000:
```bash
cd ANPR_Project
python api.py
```
