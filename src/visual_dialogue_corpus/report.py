"""Small, dependency-free pilot QA report and browser contact sheet."""

from __future__ import annotations

import html
import imghdr
import json
from collections import Counter
from pathlib import Path

from .io import read_jsonl


def build(manifest: Path, data_root: Path, report_dir: Path) -> dict:
    records = list(read_jsonl(manifest))
    originals = data_root / "originals"
    checked, invalid, total = [], [], 0
    for record in records:
        path = next(iter(originals.glob(f"{record['id'].replace(':', '_')}.*")), None)
        if path and not path.name.endswith(".part"):
            image_type = imghdr.what(path)
            total += path.stat().st_size
            checked.append({"id": record["id"], "path": str(path), "bytes": path.stat().st_size, "type": image_type})
            if image_type not in {"jpeg", "png", "gif", "webp"}:
                invalid.append({"id": record["id"], "reason": "unrecognized_magic_bytes"})
        else:
            invalid.append({"id": record["id"], "reason": "missing_file"})
    summary = {"manifest": str(manifest), "accepted": len(checked), "rejected": len(invalid), "rejections": invalid, "bytes": total, "media": dict(Counter(r["medium"] for r in records)), "cultures": dict(Counter(r["culture"] or "unknown" for r in records)), "checked": checked}
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "met-pilot-report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    cards = "".join(f'<figure><img src="file:///{Path(r["path"]).as_posix()}" loading="lazy"><figcaption>{html.escape(r["id"])}<br>{r["bytes"]:,} bytes</figcaption></figure>' for r in checked)
    (report_dir / "met-pilot-contact-sheet.html").write_text(f"<!doctype html><title>The Met pilot contact sheet</title><style>body{{font-family:sans-serif}}main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}}img{{width:100%;height:180px;object-fit:contain;background:#eee}}figure{{margin:0}}figcaption{{font-size:12px}}</style><h1>The Met pilot — {len(checked)} verified files</h1><main>{cards}</main>", encoding="utf-8")
    return summary
