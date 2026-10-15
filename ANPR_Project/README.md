# 🚗 Automatic Number Plate Recognition (ANPR) & Basic Vehicle Detection System

A beginner-friendly Computer Vision project built with Python, OpenCV, EasyOCR, and YOLOv8.

---

## 📌 Project Objective

This project implements a prototype system that can:
1. **Detect number plates** in vehicle images using image processing techniques
2. **Read plate text** using Optical Character Recognition (OCR)
3. **Detect vehicles** (car, motorcycle, bus, truck) using a pretrained YOLO model

> **Note:** This is an educational prototype. Accuracy depends on image quality, lighting, plate angle, and plate format. It is NOT a production-grade system.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Programming language |
| **OpenCV** | Image reading, preprocessing, contour detection, drawing |
| **NumPy** | Array/matrix operations for image data |
| **EasyOCR** | Optical Character Recognition (reading text from images) |
| **YOLOv8 (ultralytics)** | Object detection for vehicles |
| **Matplotlib** | Optional result visualization |

---

## 📁 Project Structure

```
ANPR_Project/
│
├── main.py                 # Entry point — runs the complete pipeline
├── preprocessing.py        # Image preprocessing (resize, grayscale, blur, edges)
├── plate_detector.py       # Number plate detection using contours
├── ocr.py                  # OCR using EasyOCR
├── vehicle_detector.py     # Vehicle detection using YOLOv8
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── VIVA_NOTES.md           # Viva preparation Q&A
│
├── input_images/           # Put your test images here
├── output_images/          # Results are saved here
└── sample_data/            # Cropped plate images are saved here
```

---

## 🔄 How ANPR Works — Complete Workflow

### Step 1: Image Preprocessing

Raw images need to be cleaned before analysis:

1. **Read Image** — OpenCV loads the image as a NumPy array (height × width × 3 channels)
2. **Resize** — Scale to a standard width (800px) while keeping the aspect ratio
3. **Grayscale** — Convert from 3 color channels (BGR) to 1 channel (brightness only). This removes color information we don't need and makes processing faster.
4. **Gaussian Blur** — Smooth the image to reduce noise. Noise creates false edges that confuse the edge detector.
5. **Canny Edge Detection** — Find boundaries/edges in the image. Pixels where brightness changes sharply become white, everything else becomes black.
6. **Thresholding** — Convert to pure black and white using Otsu's method. Useful for OCR preprocessing.

### Step 2: Number Plate Detection

Uses contour analysis (no neural network):

1. **Find Contours** — OpenCV traces the outlines of shapes in the edge image
2. **Approximate Polygons** — Simplify each contour to a polygon with fewer points
3. **Filter Candidates** — Keep only shapes that:
   - Have 4 corners (rectangles)
   - Have a width-to-height ratio of 1.5 to 7.0 (plates are wider than tall)
   - Have an area between 0.5% and 15% of the image
4. **Select Best Match** — Take the largest valid rectangle as the plate
5. **Crop** — Cut out the plate region from the original image

### Step 3: OCR (Optical Character Recognition)

Uses EasyOCR to read text from the cropped plate:

1. **Preprocess** — Convert to grayscale, enlarge if small, apply bilateral filter and threshold
2. **Run EasyOCR** — The pretrained model detects and recognizes characters
3. **Clean Output** — Remove special characters, extra spaces, convert to uppercase
4. **Return Result** — Plate text + confidence score (0.0 to 1.0)

### Step 4: Vehicle Detection

Uses a pretrained YOLOv8 nano model:

1. **Load Model** — `yolov8n.pt` (6 MB, pretrained on COCO dataset)
2. **Run Inference** — YOLO processes the entire image in one pass
3. **Filter Results** — Keep only vehicle classes: car, motorcycle, bus, truck
4. **Draw Boxes** — Add colored bounding boxes and labels to the image

### Step 5: Output

- Annotated image saved to `output_images/` with all detections drawn
- Cropped plate saved to `sample_data/`
- Clean summary printed to the terminal

---

## ⚙️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone or download this project**

2. **Open a terminal in the project folder** (or use VS Code terminal)

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **First run will download models automatically:**
   - YOLOv8 nano model (~6 MB)
   - EasyOCR English model (~100 MB)

---

## ▶️ How to Run

### Process all images in the input folder:
```bash
python main.py
```

### Process a single image:
```bash
python main.py path/to/your/image.jpg
```

### Test individual modules:
```bash
python preprocessing.py input_images/car1.jpg
python plate_detector.py input_images/car1.jpg
python ocr.py sample_data/detected_plate.jpg
python vehicle_detector.py input_images/car1.jpg
```

---

## 📸 Expected Output

### Terminal Output:
```
============================================================
🚗 AUTOMATIC NUMBER PLATE RECOGNITION (ANPR)
   & Basic Vehicle Detection System
============================================================

Found 1 image(s) in 'input_images/'

--- Loading YOLO Model ---
[INFO] Loading YOLO model: yolov8n.pt
[INFO] YOLO model loaded successfully!

============================================================
Processing: car1.jpg
============================================================

--- Step 1: Preprocessing ---
[INFO] Image loaded successfully
[INFO] Converted to grayscale
[INFO] Applied Gaussian blur
[INFO] Applied Canny edge detection

--- Step 2: Number Plate Detection ---
[INFO] Number plate candidate found!
[INFO] Plate detected at: x=150, y=280, width=180, height=45

--- Step 3: OCR ---
[INFO] Running OCR on plate image...
  [OCR] Detected: 'ABC 1234' (confidence: 0.87)
[INFO] Final plate text: 'ABC 1234'

--- Step 4: Vehicle Detection ---
  [YOLO] Detected: Car (confidence: 0.92)

============================================================
📋 RESULTS SUMMARY
============================================================
Image: car1.jpg
----------------------------------------

🚗 Vehicles Detected:
   1. Car (confidence: 92%)

🔢 Number Plate: ABC 1234
📊 OCR Confidence: 87%

💾 Output saved: output_images/car1_result.jpg
============================================================
```

### Output Image:
- Green rectangle around the detected number plate
- Plate text displayed near the plate
- Colored bounding boxes around detected vehicles
- Vehicle type and confidence labels

---

## ⚠️ Limitations

This is a **prototype** with the following limitations:

| Limitation | Explanation |
|-----------|-------------|
| **Image quality** | Blurry, dark, or low-resolution images reduce accuracy |
| **Plate angle** | Only works well on front-facing, roughly horizontal plates |
| **Plate format** | Tested primarily with standard alphanumeric plates |
| **Lighting** | Extreme shadows or glare can hide plate edges |
| **Occlusion** | Partially hidden plates cannot be detected |
| **Multiple plates** | Only detects the most prominent plate in an image |
| **No real-time** | Processes static images, not live video feeds |
| **OCR errors** | Similar-looking characters (O vs 0, I vs 1) may be confused |
| **Contour method** | Not as robust as deep-learning-based plate detectors |

---

## 🚀 Future Improvements

1. **Deep Learning Plate Detection** — Use a YOLO model trained specifically on license plates for better accuracy
2. **Video Processing** — Process live video from a webcam or traffic camera
3. **Database Integration** — Store detected plates in a database for lookup
4. **Multi-plate Detection** — Detect multiple plates in one image
5. **Plate Format Validation** — Verify that detected text matches a known plate format (e.g., Pakistani plates)
6. **GUI Application** — Build a simple desktop interface using Tkinter or PyQt
7. **Night Vision** — Apply histogram equalization and adaptive thresholding for nighttime images
8. **Speed Tracking** — Combine with a speed estimation system
9. **Cloud Deployment** — Deploy as a web API using Flask or FastAPI
10. **Better OCR** — Use Tesseract OCR with custom training for specific plate fonts

---

## 📚 References

- [OpenCV Documentation](https://docs.opencv.org/)
- [EasyOCR GitHub](https://github.com/JaidedAI/EasyOCR)
- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [COCO Dataset Classes](https://cocodataset.org/)

---

## 👨‍💻 Author

BSCS Internship Project — Automatic Number Plate Recognition (ANPR)

---
