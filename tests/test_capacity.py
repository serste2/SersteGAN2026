import tempfile
import unittest
from pathlib import Path

from visual_dialogue_corpus.capacity import plan


class CapacityTests(unittest.TestCase):
    def test_plan_accounts_for_every_target_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = plan(Path(directory), 2_000_000, thumbnail_bytes=40_000)
        self.assertEqual(result["thumbnail_bytes"], 80_000_000_000)
