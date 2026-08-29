import unittest

from visual_dialogue_corpus.schema import validate


class SchemaTests(unittest.TestCase):
    def test_rejects_late_historical_artist(self) -> None:
        record = {"corpus": "historical_vision", "id": "x:1", "image_url": "https://x", "source_url": "https://x", "rights": "Public Domain", "rights_url": "https://x", "source": "x", "source_object_id": "1", "title": "x", "artist": "x", "artist_death_year": 1980, "anonymous": False, "object_date": "", "object_begin_year": 0, "object_end_year": 0, "medium": "painting", "culture": "", "department": "", "classification": "Painting"}
        self.assertIn("invalid:artist_death_year", validate(record))

    def test_loop_requires_target(self) -> None:
        record = {"corpus": "visual_dialogue", "id": "dada:1", "image_url": "https://x", "source_url": "https://x", "rights": "CC0", "rights_url": "https://x", "source": "dada", "source_object_id": "1", "conversation_id": "c", "position": 1, "parent_id": "", "author_id": "a", "relation": "loop", "is_museum_prompt": False, "is_sitm": True}
        self.assertIn("missing:target_id", validate(record))
