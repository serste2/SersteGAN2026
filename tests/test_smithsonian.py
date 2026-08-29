import unittest

from visual_dialogue_corpus.smithsonian import canonical_records


class SmithsonianTests(unittest.TestCase):
    def test_accepts_cc0_historical_art_image(self) -> None:
        raw = {"id":"x","unitCode":"SAAM","hash":"h","content":{"freetext":{"name":[{"label":"Artist","content":"A, died 1900"}],"objectType":[{"label":"Type","content":"Painting"}],"objectRights":[{"label":"Restrictions & Rights","content":"CC0"}]},"indexedStructured":{},"descriptiveNonRepeating":{"record_ID":"saam_1","record_link":"https://example","title":{"content":"Work"},"metadata_usage":{"access":"CC0"},"online_media":{"media":[{"type":"Images","idsId":"IMG1","usage":{"access":"CC0"},"thumbnail":"https://thumb","content":"https://original"}]}}}}
        records, reason = canonical_records(raw)
        self.assertIsNone(reason)
        self.assertEqual(records[0]["rights"], "CC0-1.0")

    def test_rejects_living_or_unknown_death_artist(self) -> None:
        raw = {"content":{"freetext":{"name":[{"label":"Artist","content":"Living Artist, born 1980"}],"objectType":[{"label":"Type","content":"Painting"}]},"descriptiveNonRepeating":{}}}
        self.assertEqual(canonical_records(raw)[1], "artist_rights_cutoff")
