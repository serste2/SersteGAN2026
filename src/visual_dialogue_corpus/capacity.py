"""Storage budget calculator for metadata-first visual corpora."""

from __future__ import annotations

import shutil
from pathlib import Path


def plan(root: Path, target: int, thumbnail_bytes: int = 60_000, embedding_dim: int = 768) -> dict:
    free = shutil.disk_usage(root).free
    thumbnails = target * thumbnail_bytes
    embeddings = target * embedding_dim * 2
    manifests = target * 1_500
    index_overhead = int(embeddings * 1.5)
    total = thumbnails + embeddings + manifests + index_overhead
    return {
        "target_images": target, "free_bytes": free, "thumbnail_bytes_each": thumbnail_bytes,
        "thumbnail_bytes": thumbnails, "embedding_bytes_fp16": embeddings, "manifest_bytes_estimate": manifests,
        "index_bytes_estimate": index_overhead, "total_bytes_estimate": total, "fits_with_20_percent_reserve": total <= free * 0.8,
    }
