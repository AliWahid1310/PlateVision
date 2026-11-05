# 🎓 ANPR Defense & Viva Preparation Notes

## 1. What is Homography and Perspective Transformation?
Homography is an invertible mapping between two planar projective surfaces. When a vehicle's license plate is captured from an angle, characters appear trapezoidal.
Using `cv2.getPerspectiveTransform()` and `cv2.warpPerspective()`, we compute a 3x3 transformation matrix $M$ from 4 detected corner points to an orthogonal bounding rectangle $[0, 0, W, H]$, virtually rotating the camera straight in front of the plate.

## 2. Why use Auto-Canny instead of static thresholds?
Static values (e.g. 50, 150) degrade when images have uneven brightness. Auto-Canny computes thresholds relative to the image's median intensity $v$, guaranteeing optimal gradient detection across sunlight, overcast skies, and night scenes.

## 3. How does YOLOv8 Object Detection work?
YOLOv8 uses a CNN-based anchor-free backbone (modified CSPDarknet53) with C2f modules that fuse feature maps across spatial scales. It performs single-pass bounding box regression and classification simultaneously, executing at 60+ FPS on GPU.

## 4. How is dominant vehicle color extracted?
Color is determined by converting the vehicle bounding box to HSV space, masking out tire/windshield areas, and calculating color histogram coverage against calibrated ranges.
