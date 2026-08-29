"""Manifest validation for historical and conversational visual-dialogue records."""

from __future__ import annotations

from typing import Any

COMMON = {"corpus", "id", "image_url", "source_url", "rights", "rights_url", "source", "source_object_id"}
HISTORICAL = {"title", "artist", "artist_death_year", "anonymous", "object_date", "object_begin_year", "object_end_year", "medium", "culture", "department", "classification"}
RELATIONS = {"echo", "transform", "substitute", "consequence", "perspective", "contradict", "metaphor", "escalate", "question", "loop", "unknown"}
RIGHTS = {"CC0", "CC0-1.0", "Public Domain", "Public Domain Mark", "PDM-1.0"}


def validate(record: dict[str, Any], cutoff: int = 1955) -> list[str]:
    errors = [f"missing:{key}" for key in sorted(COMMON - record.keys())]
    corpus = record.get("corpus")
    if corpus not in {"historical_vision", "visual_dialogue"}:
        errors.append("invalid:corpus")
    if corpus == "historical_vision":
        if record.get("rights") not in RIGHTS:
            errors.append("invalid:rights")
        errors += [f"missing:{key}" for key in sorted(HISTORICAL - record.keys())]
        if not record.get("anonymous") and (not isinstance(record.get("artist_death_year"), int) or record["artist_death_year"] > cutoff):
            errors.append("invalid:artist_death_year")
    if corpus == "visual_dialogue":
        if not record.get("rights"):
            errors.append("missing:rights")
        for field in ("conversation_id", "position", "parent_id", "author_id", "relation", "is_museum_prompt", "is_sitm"):
            if field not in record:
                errors.append(f"missing:{field}")
        if record.get("relation") not in RELATIONS:
            errors.append("invalid:relation")
        if record.get("relation") == "loop" and not record.get("target_id"):
            errors.append("missing:target_id")
    return errors
