"""Public DADA conversation-page adapter.

DADA currently presents an expired TLS certificate to Python clients. The caller must
explicitly opt into the narrowly scoped insecure mode; it is accepted only for
https://dada.art/pa/<numeric-id> and never carries credentials.
"""

from __future__ import annotations

import ssl
import json
import time
from http.client import HTTPException
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class ConversationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.turns: list[dict] = []
        self.current: dict | None = None
        self.in_name = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "article" and values.get("data-activity"):
            self.current = {"activity_id": values["data-activity"], "classes": values.get("class", "")}
        elif self.current is not None and tag == "img" and not self.current.get("image_url"):
            self.current["image_url"] = values.get("src")
        elif self.current is not None and tag == "a" and (values.get("href") or "").startswith("/portraits/"):
            self.current.setdefault("author_id", values["href"].rsplit("/", 1)[-1])
        elif self.current is not None and tag == "h4":
            self.in_name = True

    def handle_data(self, data: str) -> None:
        if self.current is not None and self.in_name and data.strip():
            self.current["author_name"] = data.strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "h4":
            self.in_name = False
        elif tag == "article" and self.current is not None:
            self.turns.append(self.current)
            self.current = None


def _public_conversation_url(seed: str) -> tuple[str, str]:
    seed = seed.strip()
    if seed.isdigit():
        seed = f"https://dada.art/pa/{seed}"
    parsed = urlparse(seed)
    parts = parsed.path.strip("/").split("/")
    if parsed.scheme != "https" or parsed.hostname != "dada.art" or len(parts) != 2 or parts[0] != "pa" or not parts[1].isdigit():
        raise ValueError("DADA seed must be https://dada.art/pa/<numeric-id>")
    return seed, parts[1]


def collect(seeds: list[str], allow_expired_certificate: bool = False) -> list[dict]:
    if not allow_expired_certificate:
        raise ValueError("DADA certificate is currently invalid; pass explicit insecure opt-in for public pages only")
    context = ssl._create_unverified_context()
    records: list[dict] = []
    seen: set[str] = set()
    for seed in seeds:
        source_url, conversation_id = _public_conversation_url(seed)
        request = Request(source_url, headers={"User-Agent": "visual-dialogue-corpus/0.1"})
        with urlopen(request, context=context, timeout=45) as response:
            body = response.read().decode("utf-8", "replace")
        parser = ConversationParser()
        parser.feed(body)
        previous_id: str | None = None
        for position, turn in enumerate(parser.turns):
            activity_id = turn["activity_id"]
            if activity_id in seen or not turn.get("image_url"):
                continue
            seen.add(activity_id)
            records.append({
                "corpus": "visual_dialogue", "id": f"dada:{activity_id}", "image_url": turn["image_url"],
                "source_url": source_url, "rights": "DADA platform terms - review required",
                "rights_url": "https://dada.art/", "source": "dada", "source_object_id": activity_id,
                "conversation_id": f"dada:{conversation_id}", "position": position, "parent_id": f"dada:{previous_id}" if previous_id else None,
                "author_id": turn.get("author_id") or "unknown", "author_name": turn.get("author_name") or "unknown",
                "relation": "unknown", "target_id": None, "is_museum_prompt": False, "is_sitm": False,
                "training_eligible": False, "structure_evidence": "rendered_sequence",
                "retrieved_at": datetime.now(UTC).isoformat(),
            })
            previous_id = activity_id
    return records


def crawl_range(start: int, end: int, output: Path, ledger: Path, delay: float = 0.75) -> dict:
    """Scan an inclusive numeric range with append-only output and a resumable ledger."""
    if start < 1 or end < start or delay < 0.25:
        raise ValueError("require 1 <= start <= end and delay >= 0.25 seconds")
    output.parent.mkdir(parents=True, exist_ok=True)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    covered_page_ids: set[int] = set()
    if output.exists():
        with output.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    record = json.loads(line)
                    seen.add(record["id"])
                    covered_page_ids.add(int(record["source_object_id"]))
    completed = set()
    if ledger.exists():
        with ledger.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    event = json.loads(line)
                    if event.get("status") in {"ok", "empty", "not_found"}:
                        completed.add(int(event["page_id"]))
    stats = {"scanned": 0, "pages_with_turns": 0, "new_turns": 0, "not_found": 0, "errors": 0, "skipped_completed": 0, "skipped_covered": 0}
    with output.open("a", encoding="utf-8", newline="\n") as out, ledger.open("a", encoding="utf-8", newline="\n") as log:
        for page_id in range(start, end + 1):
            if page_id in completed:
                stats["skipped_completed"] += 1
                continue
            if page_id in covered_page_ids:
                stats["skipped_covered"] += 1
                continue
            event = {"page_id": page_id, "url": f"https://dada.art/pa/{page_id}", "checked_at": datetime.now(UTC).isoformat()}
            try:
                records = collect([str(page_id)], allow_expired_certificate=True)
                event["status"] = "ok" if records else "empty"
                event["turns"] = len(records)
                stats["scanned"] += 1
                if records:
                    stats["pages_with_turns"] += 1
                for record in records:
                    if record["id"] not in seen:
                        out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                        out.flush()
                        seen.add(record["id"])
                        covered_page_ids.add(int(record["source_object_id"]))
                        stats["new_turns"] += 1
            except HTTPError as error:
                event["status"] = "not_found" if error.code in {404, 500} else "error"
                event["error"] = f"HTTP {error.code}"
                stats["not_found" if error.code in {404, 500} else "errors"] += 1
                stats["scanned"] += 1
            except (URLError, TimeoutError, ValueError, HTTPException, OSError) as error:
                event["status"] = "error"
                event["error"] = str(error)
                stats["errors"] += 1
                stats["scanned"] += 1
            log.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
            log.flush()
            time.sleep(delay)
    return stats
