# Visual Dialogue Lantern

Code-only foundation for a system that generates a new drawing as a meaningful visual response to a prompt drawing.

## Status

Milestone 0 scaffold. No artworks, dialogue material, embeddings, checkpoints, or downloaded images are stored in this repository.

## Local setup

Copy `config/local.example.toml` to `config/local.toml` and adjust machine-specific paths. The local file is ignored by Git.

Run tests with:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

Create and verify a small The Met pilot before scaling:

```powershell
python -m visual_dialogue_corpus.cli met-manifest --query painting --limit 25 --output manifests/met-painting-smoke.jsonl
python -m visual_dialogue_corpus.cli validate manifests/met-painting-smoke.jsonl
python -m visual_dialogue_corpus.cli download manifests/met-painting-smoke.jsonl --data-root data/historical_vision/met
python -m visual_dialogue_corpus.cli report manifests/met-painting-smoke.jsonl --data-root data/historical_vision/met --output-dir reports
```

## Data policy

Canonical manifests live in `manifests/`. Originals, derived data, indexes, checkpoints, and logs live under the local `data/` root and are excluded from Git.
