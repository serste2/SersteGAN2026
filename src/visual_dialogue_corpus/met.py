"""The Met Collection API adapter; metadata only unless the downloader is invoked."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://collectionapi.metmuseum.org/public/collection/v1"
ALLOWED_MEDIUM = ("painting", "watercolor", "gouache", "pastel", "fresco", "manuscript", "drawing")


def _get(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "visual-dialogue-corpus/0.1"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def _death_year(value: str) -> int | None:
    years = [int(year) for year in re.findall(r"(?<!\d)(1[0-9]{3}|20[0-9]{2})(?!\d)", value or "")]
    return max(years) if years else None


def _record(obj: dict) -> dict | None:
    medium = obj.get("medium") or ""
    classification = obj.get("classification") or ""
    if not obj.get("isPublicDomain") or not obj.get("primaryImage"):
        return None
    if not any(term in f"{medium} {classification}".lower() for term in ALLOWED_MEDIUM):
        return None
    anonymous = not bool(obj.get("artistDisplayName"))
    death_year = _death_year(obj.get("artistEndDate", ""))
    if not anonymous and (death_year is None or death_year > 1955):
        return None
    object_id = str(obj["objectID"])
    return {
        "corpus": "historical_vision", "id": f"met:{object_id}", "image_url": obj["primaryImage"],
        "source_url": obj.get("objectURL") or f"https://www.metmuseum.org/art/collection/search/{object_id}",
        "rights": "Public Domain", "rights_url": "https://www.metmuseum.org/information/terms-and-conditions",
        "source": "met", "source_object_id": object_id, "title": obj.get("title") or "Untitled",
        "artist": obj.get("artistDisplayName") or "Anonymous", "artist_death_year": death_year,
        "anonymous": anonymous, "object_date": obj.get("objectDate") or "", "object_begin_year": obj.get("objectBeginDate"),
        "object_end_year": obj.get("objectEndDate"), "medium": medium, "culture": obj.get("culture") or "",
        "department": obj.get("department") or "", "classification": classification,
        "retrieved_at": datetime.now(UTC).isoformat(),
    }


def collect(query: str, limit: int) -> list[dict]:
    search = _get(f"{BASE}/search?" + urlencode({"hasImages": "true", "q": query}))
    records: list[dict] = []
    for object_id in search.get("objectIDs") or []:
        candidate = _record(_get(f"{BASE}/objects/{object_id}"))
        if candidate:
            records.append(candidate)
        if len(records) >= limit:
            break
    return records
