# Visual Dialogue Lantern

Code-only foundation for a system that generates a new drawing as a meaningful visual response to a prompt drawing.

## Draw now

The local Visual Dialogue prototype is available today. Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_visual_dialogue.ps1
```

It opens a drawing canvas at `http://127.0.0.1:4173`. Draw a gesture, select a dialogue relation, generate a response, continue to a second turn, and download the result.

The current engine is an honestly labelled procedural generator, not a trained GAN checkpoint. It proves the interaction and dialogue protocol while corpus collection and model work continue.

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

Collect known public DADA conversations without login. DADA currently has an expired
TLS certificate, so the exception must be explicit and is restricted in code to public
`https://dada.art/pa/<id>` pages:

```powershell
python -m visual_dialogue_corpus.cli dada-manifest --seed 133700 --seed 133752 --seed 133755 --allow-expired-certificate --output data/visual_dialogue/dada-seeds.jsonl
python -m visual_dialogue_corpus.cli dada-crawl --start 1 --end 1000 --delay 0.75 --output data/visual_dialogue/dada-public.jsonl --ledger data/logs/dada-crawl.jsonl
```

DADA records are marked `training_eligible=false` until rights for model training are confirmed.

The DADA number is a global activity ID. Opening a reply ID renders the remaining suffix
of that chain, so the range crawler records all rendered turns and skips covered IDs when
it later reaches them.

## Data policy

Canonical manifests live in `manifests/`. Originals, derived data, indexes, checkpoints, and logs live under the local `data/` root and are excluded from Git.
