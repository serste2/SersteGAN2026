from __future__ import annotations

import argparse
import json
from pathlib import Path

from .download import download
from .io import read_jsonl, write_jsonl
from .met import collect
from .report import build
from .schema import validate


def main() -> None:
    parser = argparse.ArgumentParser(prog="visual-dialogue-corpus")
    commands = parser.add_subparsers(dest="command", required=True)
    met = commands.add_parser("met-manifest")
    met.add_argument("--query", default="painting")
    met.add_argument("--limit", type=int, default=25)
    met.add_argument("--output", type=Path, required=True)
    check = commands.add_parser("validate")
    check.add_argument("manifest", type=Path)
    fetch = commands.add_parser("download")
    fetch.add_argument("manifest", type=Path)
    fetch.add_argument("--data-root", type=Path, required=True)
    fetch.add_argument("--limit", type=int, default=25)
    report = commands.add_parser("report")
    report.add_argument("manifest", type=Path)
    report.add_argument("--data-root", type=Path, required=True)
    report.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "met-manifest":
        print(json.dumps({"accepted": write_jsonl(args.output, iter(collect(args.query, args.limit))), "output": str(args.output)}))
    elif args.command == "validate":
        invalid = [{"id": r.get("id"), "errors": validate(r)} for r in read_jsonl(args.manifest) if validate(r)]
        print(json.dumps({"invalid": invalid, "valid": not invalid}))
        if invalid:
            raise SystemExit(1)
    elif args.command == "download":
        results, failures = [], []
        for _, record in zip(range(args.limit), read_jsonl(args.manifest)):
            try:
                results.append(download(record, args.data_root))
            except RuntimeError as error:
                failures.append({"id": record["id"], "error": str(error)})
        print(json.dumps({"downloaded": len(results), "failed": failures, "bytes": sum(r["bytes"] for r in results)}))
        if failures:
            raise SystemExit(1)
    else:
        print(json.dumps(build(args.manifest, args.data_root, args.output_dir)))


if __name__ == "__main__":
    main()
