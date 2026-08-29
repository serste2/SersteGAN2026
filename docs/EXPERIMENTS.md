# Experiments

## 2026-08-29 — The Met smoke pilot

- Manifest validation: 25 valid / 0 invalid.
- Download QA: 25 JPEGs recognized from magic bytes; 77,460,327 bytes total.
- Artifacts: local JSON report and browser contact sheet in `reports/`.
- Observation: an interrupted initial transfer exposed the need for retries and idempotent re-runs; both are now implemented.
