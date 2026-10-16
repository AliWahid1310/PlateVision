# Image Preprocessing & Filter Tuning Guide

## Filter Rationale
1. **Aspect-Ratio Resizing**: Normalizing width to 800px ensures consistent edge filter response regardless of source camera resolution.
2. **CLAHE**: Solves harsh outdoor glare and twilight conditions where regular Otsu thresholding under-segments text.
3. **Auto-Canny**: Derives threshold bounds `[max(0, (1 - s) * median), min(255, (1 + s) * median)]`, adapting to dynamic brightness conditions.
4. **Bilateral Smoothing**: Suppresses bumper textures, grille lines, and road noise while retaining crisp character outlines.
