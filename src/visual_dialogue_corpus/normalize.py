"""Atomic image normalization and exact/perceptual hashing."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image, ImageOps


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _average_hash(image: Image.Image) -> str:
    sample = ImageOps.grayscale(image).resize((8, 8), Image.Resampling.LANCZOS)
    values = list(sample.getdata())
    average = sum(values) / len(values)
    bits = "".join("1" if value >= average else "0" for value in values)
    return f"{int(bits, 2):016x}"


def normalize_directory(source: Path, output: Path, ledger: Path, max_side: int = 384, quality: int = 80) -> dict:
    if max_side < 128 or quality < 40 or quality > 95:
        raise ValueError("unsafe normalization settings")
    output.mkdir(parents=True, exist_ok=True)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    stats = {"processed": 0, "skipped": 0, "failed": 0, "source_bytes": 0, "normalized_bytes": 0}
    with ledger.open("a", encoding="utf-8", newline="\n") as log:
        for path in sorted(item for item in source.iterdir() if item.is_file() and not item.name.endswith(".part")):
            target = output / f"{path.stem}.webp"
            if target.exists():
                stats["skipped"] += 1
                continue
            partial = target.with_suffix(".webp.part")
            try:
                with Image.open(path) as opened:
                    image = ImageOps.exif_transpose(opened).convert("RGB")
                    source_size = image.size
                    image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
                    image.save(partial, format="WEBP", quality=quality, method=6)
                    perceptual_hash = _average_hash(image)
                    normalized_size = image.size
                partial.replace(target)
                event = {"source": str(path), "normalized": str(target), "source_bytes": path.stat().st_size,
                         "normalized_bytes": target.stat().st_size, "source_size": source_size, "normalized_size": normalized_size,
                         "sha256": _sha256(target), "phash": perceptual_hash, "max_side": max_side, "quality": quality,
                         "normalized_at": datetime.now(UTC).isoformat()}
                log.write(json.dumps(event, sort_keys=True) + "\n")
                log.flush()
                stats["processed"] += 1
                stats["source_bytes"] += path.stat().st_size
                stats["normalized_bytes"] += target.stat().st_size
            except Exception as error:
                partial.unlink(missing_ok=True)
                stats["failed"] += 1
                log.write(json.dumps({"source": str(path), "error": str(error), "normalized_at": datetime.now(UTC).isoformat()}, sort_keys=True) + "\n")
                log.flush()
    if stats["processed"]:
        stats["average_normalized_bytes"] = round(stats["normalized_bytes"] / stats["processed"])
        stats["compression_ratio"] = round(stats["normalized_bytes"] / stats["source_bytes"], 4)
    return stats
