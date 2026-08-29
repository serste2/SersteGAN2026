"""Measured visual vocabulary and prompt-response deltas for DADA sequences."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

from PIL import Image, ImageOps, ImageStat

from .io import read_jsonl


def _distance(a, b) -> int:
    return sum(abs(a[i] - b[i]) for i in range(3))


def measure(path: Path, size: int = 128) -> dict:
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (size, size), image.getpixel((0, 0)))
        canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
    corners = [canvas.getpixel((0, 0)), canvas.getpixel((size - 1, 0)), canvas.getpixel((0, size - 1)), canvas.getpixel((size - 1, size - 1))]
    background = min(corners, key=lambda candidate: sum(_distance(candidate, other) for other in corners))
    points, colors = [], []
    edge = Counter()
    for y in range(size):
        for x in range(size):
            color = canvas.getpixel((x, y))
            if _distance(color, background) > 55:
                points.append((x, y))
                colors.append(color)
                if x <= 1: edge["left"] += 1
                if x >= size - 2: edge["right"] += 1
                if y <= 1: edge["top"] += 1
                if y >= size - 2: edge["bottom"] += 1
    if not points:
        return {"density": 0.0, "background_rgb": background, "empty": True}
    xs, ys = zip(*points)
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    var_x = sum((x - cx) ** 2 for x in xs) / len(xs)
    var_y = sum((y - cy) ** 2 for y in ys) / len(ys)
    cov_xy = sum((x - cx) * (y - cy) for x, y in points) / len(points)
    orientation = math.degrees(0.5 * math.atan2(2 * cov_xy, var_x - var_y))
    grayscale = ImageOps.grayscale(canvas)
    histogram = grayscale.histogram()
    total = sum(histogram)
    entropy = -sum((count / total) * math.log2(count / total) for count in histogram if count)
    mean_color = tuple(round(sum(color[i] for color in colors) / len(colors)) for i in range(3))
    return {
        "density": round(len(points) / (size * size), 6), "background_rgb": background, "mean_mark_rgb": mean_color,
        "centroid_x": round(cx / (size - 1), 6), "centroid_y": round(cy / (size - 1), 6),
        "bbox_left": round(min(xs) / (size - 1), 6), "bbox_top": round(min(ys) / (size - 1), 6),
        "bbox_right": round(max(xs) / (size - 1), 6), "bbox_bottom": round(max(ys) / (size - 1), 6),
        "orientation_degrees": round(orientation, 3), "entropy": round(entropy, 4),
        "touch_left": edge["left"] > 0, "touch_right": edge["right"] > 0,
        "touch_top": edge["top"] > 0, "touch_bottom": edge["bottom"] > 0, "empty": False,
    }


def compile_visual_grammar(manifest: Path, pairs: Path, images: Path, features_out: Path, deltas_out: Path, report: Path) -> dict:
    records = {record["id"]: record for record in read_jsonl(manifest)}
    features = {}
    missing = 0
    features_out.parent.mkdir(parents=True, exist_ok=True)
    with features_out.open("w", encoding="utf-8", newline="\n") as output:
        for record_id in sorted(records):
            path = images / f"{record_id.replace(':', '_')}.webp"
            if not path.exists():
                missing += 1
                continue
            feature = measure(path)
            feature["id"] = record_id
            features[record_id] = feature
            output.write(json.dumps(feature, sort_keys=True) + "\n")
    numeric = ("density", "centroid_x", "centroid_y", "bbox_left", "bbox_top", "bbox_right", "bbox_bottom", "orientation_degrees", "entropy")
    delta_sums = Counter()
    edge_continuations = 0
    compiled_pairs = 0
    deltas_out.parent.mkdir(parents=True, exist_ok=True)
    with deltas_out.open("w", encoding="utf-8", newline="\n") as output:
        for pair in read_jsonl(pairs):
            prompt, response = features.get(pair["prompt_id"]), features.get(pair["response_id"])
            if not prompt or not response or prompt.get("empty") or response.get("empty"):
                continue
            deltas = {field: round(response[field] - prompt[field], 6) for field in numeric}
            for field, value in deltas.items():
                delta_sums[field] += abs(value)
            seamless = bool(prompt["touch_right"] and response["touch_left"])
            edge_continuations += int(seamless)
            output.write(json.dumps({**pair, "deltas": deltas, "right_to_left_continuation": seamless}, sort_keys=True) + "\n")
            compiled_pairs += 1
    summary = {
        "manifest_records": len(records), "measured_images": len(features), "missing_images": missing,
        "measured_pairs": compiled_pairs, "right_to_left_continuations": edge_continuations,
        "mean_absolute_delta": {field: round(total / compiled_pairs, 6) if compiled_pairs else None for field, total in delta_sums.items()},
        "interpretation_gate": "measured deltas only; semantic relation labels require review",
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
