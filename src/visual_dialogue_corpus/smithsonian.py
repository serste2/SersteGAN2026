"""Streaming adapter for the Smithsonian Open Access bulk JSONL release."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import UTC, datetime
from urllib.request import Request, urlopen

UNIT_INDEX = "https://smithsonian-open-access.s3-us-west-2.amazonaws.com/metadata/edan/{unit}/index.txt"
RIGHTS_URL = "https://www.si.edu/openaccess"
ART_TYPES = ("painting", "drawing", "graphic", "print", "sculpt", "decorative", "photograph", "textile", "ceramic", "illustrat")


def _lines(url: str):
    request = Request(url, headers={"User-Agent": "visual-dialogue-corpus/0.2"})
    with urlopen(request, timeout=60) as response:
        for raw in response:
            line = raw.decode("utf-8", "replace").strip()
            if line:
                yield line


def shard_urls(unit: str) -> list[str]:
    unit = unit.lower()
    if not re.fullmatch(r"[a-z0-9]+", unit):
        raise ValueError("invalid Smithsonian unit")
    return list(_lines(UNIT_INDEX.format(unit=unit)))


def _field(items: list[dict] | None, label: str) -> str:
    for item in items or []:
        if item.get("label") == label:
            return item.get("content") or ""
    return ""


def _artist(name_items: list[dict] | None) -> tuple[str, int | None, bool]:
    value = _field(name_items, "Artist") or "Unidentified"
    anonymous = value.strip().lower() in {"unidentified", "unknown", "anonymous"}
    if anonymous:
        return value, None, True
    died = re.search(r"(?:died|deceased)[^0-9]*(\d{3,4})", value, re.IGNORECASE)
    return value, int(died.group(1)) if died else None, False


def _year_range(value: str) -> tuple[int | None, int | None]:
    years = [int(year) for year in re.findall(r"(?<!\d)(\d{3,4})(?!\d)", value or "")]
    return (min(years), max(years)) if years else (None, None)


def _media_url(media: dict, label: str) -> str | None:
    for resource in media.get("resources") or []:
        if resource.get("label") == label:
            return resource.get("url")
    return None


def canonical_records(raw: dict, cutoff: int = 1955) -> tuple[list[dict], str | None]:
    content = raw.get("content") or {}
    free = content.get("freetext") or {}
    indexed = content.get("indexedStructured") or {}
    desc = content.get("descriptiveNonRepeating") or {}
    metadata_rights = (desc.get("metadata_usage") or {}).get("access")
    classification = _field(free.get("objectType"), "Type") or " ".join(indexed.get("object_type") or [])
    if not any(term in classification.lower() for term in ART_TYPES):
        return [], "not_art_type"
    artist, death_year, anonymous = _artist(free.get("name"))
    if not anonymous and (death_year is None or death_year > cutoff):
        return [], "artist_rights_cutoff"
    date_text = _field(free.get("date"), "Date")
    begin_year, end_year = _year_range(date_text)
    media_items = ((desc.get("online_media") or {}).get("media") or [])
    accepted = []
    for media in media_items:
        if media.get("type") != "Images" or (media.get("usage") or {}).get("access") != "CC0" or metadata_rights != "CC0":
            continue
        media_id = media.get("idsId") or media.get("id")
        thumb = _media_url(media, "Screen Image") or _media_url(media, "Thumbnail Image") or media.get("thumbnail")
        original = _media_url(media, "High-resolution JPEG") or media.get("content")
        if not media_id or not thumb or not original:
            continue
        record_id = desc.get("record_ID") or raw.get("id")
        accepted.append({
            "corpus": "historical_vision", "id": f"smithsonian:{record_id}:{media_id}", "image_url": thumb,
            "original_image_url": original, "source_url": desc.get("record_link") or desc.get("guid"),
            "rights": "CC0-1.0", "rights_url": RIGHTS_URL, "source": "smithsonian", "source_object_id": media_id,
            "title": ((desc.get("title") or {}).get("content") or raw.get("title") or "Untitled"),
            "artist": artist, "artist_death_year": death_year, "anonymous": anonymous, "object_date": date_text,
            "object_begin_year": begin_year, "object_end_year": end_year, "medium": _field(free.get("physicalDescription"), "Medium"),
            "culture": " | ".join(indexed.get("culture") or []), "department": _field(free.get("setName"), "Department"),
            "classification": classification, "unit_code": raw.get("unitCode"), "source_record_hash": raw.get("hash"),
            "retrieved_at": datetime.now(UTC).isoformat(),
        })
    return (accepted, None) if accepted else ([], "no_cc0_image")


def iter_unit(unit: str, shard_limit: int | None = None, record_limit: int | None = None, stats: dict | None = None):
    counters = Counter()
    produced = 0
    urls = shard_urls(unit)
    if shard_limit is not None:
        urls = urls[:shard_limit]
    for shard_url in urls:
        counters["shards"] += 1
        for line in _lines(shard_url):
            counters["raw_records"] += 1
            records, rejection = canonical_records(json.loads(line))
            if rejection:
                counters[f"rejected:{rejection}"] += 1
            for record in records:
                yield record
                produced += 1
                counters["accepted_images"] += 1
                if record_limit is not None and produced >= record_limit:
                    if stats is not None:
                        stats.update(counters)
                    return
    if stats is not None:
        stats.update(counters)
