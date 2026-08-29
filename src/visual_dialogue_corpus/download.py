"""Atomic, hashed image downloads with append-only JSONL ledger."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(record: dict, data_root: Path, retries: int = 3) -> dict:
    target_dir = data_root / "originals"
    target_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(record["image_url"].split("?", 1)[0]).suffix.lower() or ".img"
    target = target_dir / f"{record['id'].replace(':', '_')}{suffix}"
    partial = target.with_suffix(target.suffix + ".part")
    if target.exists() and target.stat().st_size >= 1024:
        return {"id": record["id"], "path": str(target), "sha256": _sha256(target), "bytes": target.stat().st_size,
                "image_url": record["image_url"], "downloaded_at": None, "skipped_existing": True}
    request = Request(record["image_url"], headers={"User-Agent": "visual-dialogue-corpus/0.1"})
    for attempt in range(retries):
        digest = hashlib.sha256()
        try:
            with urlopen(request, timeout=60) as response, partial.open("wb") as handle:
                content_type = response.headers.get_content_type()
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    digest.update(chunk)
                    handle.write(chunk)
            break
        except (HTTPError, URLError, TimeoutError) as error:
            partial.unlink(missing_ok=True)
            if attempt == retries - 1:
                raise RuntimeError(f"download_failed:{record['id']}:{error}") from error
            time.sleep(2 ** attempt)
    if not content_type.startswith("image/") or partial.stat().st_size < 1024:
        partial.unlink(missing_ok=True)
        raise ValueError(f"invalid_image:{content_type}")
    partial.replace(target)
    result = {"id": record["id"], "path": str(target), "sha256": digest.hexdigest(), "bytes": target.stat().st_size,
              "image_url": record["image_url"], "downloaded_at": datetime.now(UTC).isoformat()}
    ledger = data_root / "download-ledger.jsonl"
    with ledger.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, sort_keys=True) + "\n")
    return result
