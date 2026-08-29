# Decisions

## 2026-08-29 — Milestone 0 scaffold

Created a code-only repository. No corpus acquisition, model training, or Unity integration has occurred.

## 2026-08-29 — Local data root on Z:

The user directed that all project work use `Z:`. The data root is therefore `Z:\\visual-dialogue-gan\\data`, protected by `.gitignore`.

## 2026-08-29 — NAS storage root

Serena superseded the earlier local-data decision for large corpus storage. Images, shards, embeddings, indexes, checkpoints, and logs now use `J:\\Sere\\visual-dialogue-corpus`. Code and lightweight manifests remain on `Z:` and GitHub. Existing pilot data on `Z:` is preserved until a separately verified migration.

## 2026-08-29 — DADA activity numbering

Public `/pa/<number>` routes use a global activity ID. Consecutive IDs may be separate conversation roots. Opening a reply ID renders the suffix of its existing chain. The crawler therefore scans upward, records the rendered chain, and skips activity IDs already covered by an earlier root page.

## 2026-08-29 — Same-day drawable prototype

The first interactive release uses a local procedural response engine behind a model-agnostic canvas workflow. It is labelled as a prototype and must not be described as a trained GAN. A future pretrained or project-trained image model will replace the response adapter without changing the core draw → response → next-turn interaction.

Canvas backgrounds are not generative choices. The response inherits the prompt's dominant corner color deterministically. On desktop, prompt and response canvases share one physical boundary with no arrow, spacer, padding, or double border at the seam.
