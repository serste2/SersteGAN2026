"""Compile exact DADA topology into ordered response pairs and corpus statistics."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from .io import read_jsonl


def compile_graph(manifest: Path, pairs_path: Path, report_path: Path) -> dict:
    conversations: dict[str, list[dict]] = defaultdict(list)
    ids = set()
    authors = Counter()
    for record in read_jsonl(manifest):
        conversations[record["conversation_id"]].append(record)
        ids.add(record["id"])
        authors[record.get("author_id") or "unknown"] += 1
    pairs_path.parent.mkdir(parents=True, exist_ok=True)
    pair_count = 0
    unresolved = 0
    lengths = Counter()
    with pairs_path.open("w", encoding="utf-8", newline="\n") as output:
        for conversation_id, turns in conversations.items():
            turns.sort(key=lambda item: item["position"])
            lengths[len(turns)] += 1
            for turn in turns:
                parent_id = turn.get("parent_id")
                if not parent_id:
                    continue
                if parent_id not in ids:
                    unresolved += 1
                pair = {
                    "conversation_id": conversation_id, "prompt_id": parent_id, "response_id": turn["id"],
                    "response_position": turn["position"], "relation": turn.get("relation", "unknown"),
                    "author_id": turn.get("author_id"), "structure_evidence": turn.get("structure_evidence"),
                }
                output.write(json.dumps(pair, ensure_ascii=False, sort_keys=True) + "\n")
                pair_count += 1
    summary = {
        "turns": len(ids), "conversations": len(conversations), "ordered_pairs": pair_count,
        "unresolved_parent_edges": unresolved, "conversation_lengths": dict(sorted(lengths.items())),
        "unique_authors": len(authors), "top_authors": authors.most_common(20),
        "semantic_relation_status": "unknown until measured/annotated; no labels inferred from appearance",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
