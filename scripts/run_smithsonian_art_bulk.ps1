$ErrorActionPreference = 'Stop'
$root = 'Z:\visual-dialogue-gan'
$python = "$root\.venv\Scripts\python.exe"
$dataRoot = 'J:\Sere\visual-dialogue-corpus'
$unitBudgets = [ordered]@{
    saam  = 300000
    npg   = 250000
    nmafa = 200000
    fsg   = 250000
    hmsg  = 100000
    chndm = 300000
    nmai  = 300000
    aaa   = 150000
    eepa  = 150000
}

foreach ($unit in $unitBudgets.Keys) {
    $budget = $unitBudgets[$unit]
    $manifest = "$root\manifests\smithsonian-$unit.jsonl"
    & $python -m visual_dialogue_corpus.cli smithsonian-bulk-manifest `
        --unit $unit `
        --record-limit $budget `
        --output $manifest
    if ($LASTEXITCODE -ne 0) { throw "Manifest failed for $unit" }

    & $python -m visual_dialogue_corpus.cli validate $manifest
    if ($LASTEXITCODE -ne 0) { throw "Validation failed for $unit" }

    & $python -m visual_dialogue_corpus.cli download $manifest `
        --data-root "$dataRoot\historical_vision\smithsonian" `
        --limit $budget
    if ($LASTEXITCODE -ne 0) { Write-Warning "Some assets failed for $unit; continuing normalization." }

    & $python -m visual_dialogue_corpus.cli normalize-images `
        --source "$dataRoot\historical_vision\smithsonian\originals" `
        --output "$dataRoot\derived\thumbnails\smithsonian" `
        --ledger "$dataRoot\logs\smithsonian-normalize.jsonl" `
        --max-side 384 `
        --quality 80
    if ($LASTEXITCODE -ne 0) { throw "Normalization failed for $unit" }
}
