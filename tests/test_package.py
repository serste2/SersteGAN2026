import unittest

from visual_dialogue_corpus import DEFAULT_ARTIST_DEATH_YEAR_CUTOFF


class PackageTests(unittest.TestCase):
    def test_default_rights_cutoff_is_conservative(self) -> None:
        self.assertEqual(DEFAULT_ARTIST_DEATH_YEAR_CUTOFF, 1955)


if __name__ == "__main__":
    unittest.main()
