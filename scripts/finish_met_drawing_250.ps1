$ErrorActionPreference = 'Stop'
$env:PYTHONPATH = 'Z:\visual-dialogue-gan\src'
$manifest = 'Z:\visual-dialogue-gan\manifests\met-drawing-250.jsonl'
$deadline = (Get-Date).AddHours(2)

while (-not (Test-Path -LiteralPath $manifest)) {
    if ((Get-Date) -ge $deadline) {
        throw 'Timed out waiting for met-drawing-250.jsonl'
    }
    Start-Sleep -Seconds 10
}

python -m visual_dialogue_corpus.cli validate $manifest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m visual_dialogue_corpus.cli download $manifest `
    --data-root 'Z:\visual-dialogue-gan\data\historical_vision\met' `
    --limit 250
exit $LASTEXITCODE
