# License Plate Contour Evaluation Heuristics

## Candidate Ranking Matrix
1. **Aspect Ratio**: Plates range from 1.8 to 6.5 width-to-height ratio. The peak target is 3.5.
2. **Area Coverage**: Candidates must occupy between 0.5% and 18% of the vehicle frame.
3. **Corner Constraint**: Approximated polygon must resolve to exactly 4 vertices (`epsilon = 0.02 * arcLength`).
4. **Solidity Check**: Ensures the polygon isn't hollow or concave.
