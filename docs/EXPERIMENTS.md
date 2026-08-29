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

## 2026-08-29 — Smithsonian bulk and NAS normalization pilot

- Bulk source: official Smithsonian SAAM shard `00.txt`.
- Raw records: 56.
- Accepted CC0 historical-art images: 38.
- Rejections: 12 non-art types, 3 no qualifying CC0 image, 3 artist cutoff/unknown death.
- Screen assets: 6,158,267 bytes total; 162,060 bytes average; up to 1200 px.
- WebP normalization: max side 384, quality 80, SHA-256 and 64-bit average perceptual hash.
- Normalized result: 487,564 bytes total; 12,831 bytes average; 92.08% reduction; zero failures.
- NAS capacity: 4.38 TB free; the two-million-image plan fits with substantial reserve.
