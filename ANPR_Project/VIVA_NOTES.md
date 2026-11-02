# 🎓 ANPR Defense & Viva Preparation Notes

## 1. What is Homography and Perspective Transformation?
Homography is an invertible mapping between two planar projective surfaces. When a vehicle's license plate is captured from an angle, characters appear trapezoidal.
Using `cv2.getPerspectiveTransform()` and `cv2.warpPerspective()`, we compute a 3x3 transformation matrix $M$ from 4 detected corner points to an orthogonal bounding rectangle $[0, 0, W, H]$, virtually rotating the camera straight in front of the plate.

## 2. Why use Auto-Canny instead of static thresholds?
Static values (e.g. 50, 150) degrade when images have uneven brightness. Auto-Canny computes thresholds relative to the image's median intensity $v$, guaranteeing optimal gradient detection across sunlight, overcast skies, and night scenes.
