# Decisions

## 2026-08-29 — Milestone 0 scaffold

Created a code-only repository. No corpus acquisition, model training, or Unity integration has occurred.

## 2026-08-29 — Local data root on Z:

The user directed that all project work use `Z:`. The data root is therefore `Z:\\visual-dialogue-gan\\data`, protected by `.gitignore`.

## 2026-08-29 — DADA activity numbering

Public `/pa/<number>` routes use a global activity ID. Consecutive IDs may be separate conversation roots. Opening a reply ID renders the suffix of its existing chain. The crawler therefore scans upward, records the rendered chain, and skips activity IDs already covered by an earlier root page.
