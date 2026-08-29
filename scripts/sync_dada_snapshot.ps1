$ErrorActionPreference = 'Stop'
$root = 'Z:\visual-dialogue-gan'
$python = "$root\.venv\Scripts\python.exe"
$dataRoot = 'J:\Sere\visual-dialogue-corpus'
$manifest = "$root\data\visual_dialogue\dada-public.jsonl"

& $python -m visual_dialogue_corpus.cli dada-graph $manifest `
    --pairs "$dataRoot\derived\pairs\dada-pairs.jsonl" `
    --report "$dataRoot\logs\dada-grammar-topology.json"
if ($LASTEXITCODE -ne 0) { throw 'DADA graph compilation failed' }

& $python -m visual_dialogue_corpus.cli download $manifest `
    --data-root "$dataRoot\visual_dialogue" `
    --limit 2000000
if ($LASTEXITCODE -ne 0) { Write-Warning 'Some DADA assets were quarantined; continuing normalization.' }

& $python -m visual_dialogue_corpus.cli normalize-images `
    --source "$dataRoot\visual_dialogue\originals" `
    --output "$dataRoot\derived\thumbnails\dada" `
    --ledger "$dataRoot\logs\dada-normalize.jsonl" `
    --max-side 384 `
    --quality 82
if ($LASTEXITCODE -ne 0) { throw 'DADA normalization failed' }

& $python -m visual_dialogue_corpus.cli visual-grammar `
    --manifest $manifest `
    --pairs "$dataRoot\derived\pairs\dada-pairs.jsonl" `
    --images "$dataRoot\derived\thumbnails\dada" `
    --features "$dataRoot\derived\sequences\dada-visual-features.jsonl" `
    --deltas "$dataRoot\derived\sequences\dada-pair-deltas.jsonl" `
    --report "$dataRoot\logs\dada-visual-grammar.json"
if ($LASTEXITCODE -ne 0) { throw 'DADA visual grammar compilation failed' }
