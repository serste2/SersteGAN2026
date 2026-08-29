# Experiments

## 2026-08-29 — The Met smoke pilot

- Manifest validation: 25 valid / 0 invalid.
- Download QA: 25 JPEGs recognized from magic bytes; 77,460,327 bytes total.
- Artifacts: local JSON report and browser contact sheet in `reports/`.
- Observation: an interrupted initial transfer exposed the need for retries and idempotent re-runs; both are now implemented.

## 2026-08-29 — Local Visual Dialogue interaction gate

- Input: a real pointer-drawn gesture on the browser canvas.
- Result: generated response using the `consequence` dialogue strategy.
- Multi-turn: response promoted to prompt and a second response generated successfully.
- Export: `visual-dialogue-turn-1.png` downloaded successfully.
- Responsive QA: 390 × 844 viewport, no horizontal overflow.
- Disclosure: UI and README explicitly identify the engine as procedural, not a trained GAN.
- Evidence: local screenshots in Git-ignored `reports/visual-dialogue-local-e2e.png` and `reports/visual-dialogue-mobile.png`.

### Border continuity check

- Desktop canvas gap: exactly `0` CSS pixels; the decorative arrow and central spacer were removed.
- Response background policy: deterministic inheritance from the prompt's dominant corner color.
- Prompt stroke reached the right border at canvas y=302.
- Echo response began at the left border at the same y=302.
- Boundary pixel matched exactly on both canvases: RGBA `[22, 18, 15, 255]`.
- The `contradict` strategy intentionally retains permission to refuse the seam.
- Evidence: local screenshot `reports/visual-dialogue-seam-e2e.png`.
