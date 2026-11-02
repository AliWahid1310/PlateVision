"""
plate_detector.py — License plate contour extraction and candidate scoring.
"""
import cv2
import numpy as np
from config import PLATE_CFG
from logger import log_info, log_warn

def find_contours(edge_image):
    contours, _ = cv2.findContours(
        edge_image.copy(),
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:35]
    log_info("PLATE_DETECTOR", f"Evaluated top {len(sorted_contours)} contours by area.")
    return sorted_contours

def calculate_candidate_score(approx, image_shape):
    """Calculates geometric fitness score for a candidate plate contour (0.0 to 1.0)."""
    if len(approx) != 4:
        return 0.0
    x, y, w, h = cv2.boundingRect(approx)
    if h == 0:
        return 0.0
    aspect_ratio = w / float(h)
    if not (PLATE_CFG.min_aspect_ratio <= aspect_ratio <= PLATE_CFG.max_aspect_ratio):
        return 0.0
    
    area = cv2.contourArea(approx)
    img_area = image_shape[0] * image_shape[1]
    area_ratio = area / float(img_area)
    if not (PLATE_CFG.min_area_ratio <= area_ratio <= PLATE_CFG.max_area_ratio):
        return 0.0

    rect_area = w * h
    solidity = area / float(rect_area) if rect_area > 0 else 0
    aspect_ideal = 3.5
    aspect_score = 1.0 - min(abs(aspect_ratio - aspect_ideal) / 3.0, 1.0)
    solidity_score = min(solidity / 0.85, 1.0)
    
    return float((aspect_score * 0.6) + (solidity_score * 0.4))

def detect_plate_contours_fallback(gray_image):
    """Fallback detector using morphological Sobel kernels when Canny contours fail."""
    grad_x = cv2.Sobel(gray_image, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    grad_x = np.absolute(grad_x)
    (min_val, max_val) = (np.min(grad_x), np.max(grad_x))
    if max_val > min_val:
        grad_x = (255 * ((grad_x - min_val) / (max_val - min_val))).astype("uint8")
    else:
        grad_x = grad_x.astype("uint8")
    
    blurred = cv2.GaussianBlur(grad_x, (5, 5), 0)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 3))
    closed = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
    _, thresh = cv2.threshold(closed, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return sorted(contours, key=cv2.contourArea, reverse=True)[:15]

def crop_plate_safe(image, bbox, padding=PLATE_CFG.crop_padding_px):
    """Safely extracts plate region with boundary clamping and padding."""
    x, y, w, h = bbox
    img_h, img_w = image.shape[:2]
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(img_w, x + w + padding)
    y2 = min(img_h, y + h + padding)
    return image[y1:y2, x1:x2].copy(), (x1, y1, x2 - x1, y2 - y1)

def order_corner_points(pts):
    """Sorts 4 corner points into: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype="float32")
    pts_reshaped = pts.reshape(4, 2)
    s = pts_reshaped.sum(axis=1)
    rect[0] = pts_reshaped[np.argmin(s)]
    rect[2] = pts_reshaped[np.argmax(s)]
    diff = np.diff(pts_reshaped, axis=1)
    rect[1] = pts_reshaped[np.argmin(diff)]
    rect[3] = pts_reshaped[np.argmax(diff)]
    return rect

def four_point_perspective_transform(image, pts):
    """Flattens skewed/angled license plates into frontal rectangles."""
    rect = order_corner_points(pts)
    (tl, tr, br, bl) = rect
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_w = max(int(width_a), int(width_b))
    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_h = max(int(height_a), int(height_b))
    if max_w == 0 or max_h == 0:
        return image
    dst = np.array([
        [0, 0],
        [max_w - 1, 0],
        [max_w - 1, max_h - 1],
        [0, max_h - 1]
    ], dtype="float32")
    m = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, m, (max_w, max_h))

def detect_plate(original_image, edge_image):
    """Scans contours, scores candidate plates, and returns the best deskewed plate."""
    contours = find_contours(edge_image)
    candidates = []
    for c in contours:
        if cv2.contourArea(c) < 300:
            continue
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, PLATE_CFG.approx_epsilon_coeff * perimeter, True)
        score = calculate_candidate_score(approx, original_image.shape)
        if score > 0:
            x, y, w, h = cv2.boundingRect(approx)
            candidates.append({"score": score, "approx": approx, "bbox": (x, y, w, h)})
    
    if not candidates:
        log_warn("PLATE_DETECTOR", "No candidate found via standard contours. Attempting morphological fallback...")
        gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY) if len(original_image.shape) == 3 else original_image
        fb_contours = detect_plate_contours_fallback(gray)
        for c in fb_contours:
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.03 * perimeter, True)
            score = calculate_candidate_score(approx, original_image.shape)
            if score > 0:
                x, y, w, h = cv2.boundingRect(approx)
                candidates.append({"score": score, "approx": approx, "bbox": (x, y, w, h)})

    if not candidates:
        log_warn("PLATE_DETECTOR", "No valid license plate detected.")
        return None, None, None

    candidates.sort(key=lambda item: item["score"], reverse=True)
    best = candidates[0]
    bbox = best["bbox"]
    if PLATE_CFG.deskew_enabled and len(best["approx"]) == 4:
        plate_crop = four_point_perspective_transform(original_image, best["approx"])
    else:
        plate_crop, bbox = crop_plate_safe(original_image, bbox)

    return plate_crop, bbox, best["approx"]

def draw_plate_overlay(image, bbox, plate_text="PLATE", confidence=0.0):
    """Draws tech-styled corner brackets and glowing detection overlay."""
    out = image.copy()
    if bbox is None:
        return out
    x, y, w, h = bbox
    color = (52, 211, 153) # Cyber Emerald
    bracket_len = min(20, w // 4, h // 4)
    # Corners
    cv2.line(out, (x, y), (x + bracket_len, y), color, 2)
    cv2.line(out, (x, y), (x, y + bracket_len), color, 2)
    cv2.line(out, (x + w, y), (x + w - bracket_len, y), color, 2)
    cv2.line(out, (x + w, y), (x + w, y + bracket_len), color, 2)
    cv2.line(out, (x, y + h), (x + bracket_len, y + h), color, 2)
    cv2.line(out, (x, y + h), (x, y + h - bracket_len), color, 2)
    cv2.line(out, (x + w, y + h), (x + w - bracket_len, y + h), color, 2)
    cv2.line(out, (x + w, y + h), (x + w, y + h - bracket_len), color, 2)
    
    label = f"{plate_text} ({confidence*100:.1f}%)" if confidence > 0 else plate_text
    cv2.putText(out, label, (x, max(18, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    return out
