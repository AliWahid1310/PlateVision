# OCR Accuracy Optimization Report

## Two-Pass OCR Heuristics
1. **Pass 1 (Otsu Binary)**: Standard bilateral filtering followed by Otsu adaptive binarization.
2. **Pass 2 (Inverted CLAHE)**: Triggered when pass 1 yields confidence below 55%. Inverting pixel intensities handles inverted white-on-black or yellow-on-black commercial plates.
3. **Disambiguation Rules**: Disambiguates visually similar glyphs (e.g. `O` vs `0`, `B` vs `8`) using provincial syntax positional constraints.
