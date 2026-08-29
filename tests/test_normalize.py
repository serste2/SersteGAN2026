import tempfile
import unittest
from pathlib import Path

from PIL import Image

from visual_dialogue_corpus.normalize import normalize_directory


class NormalizeTests(unittest.TestCase):
    def test_normalizes_and_hashes_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "source", root / "output"
            source.mkdir()
            Image.new("RGB", (800, 600), "red").save(source / "sample.jpg")
            result = normalize_directory(source, output, root / "ledger.jsonl", max_side=256)
            with Image.open(output / "sample.webp") as image:
                self.assertEqual(image.size, (256, 192))
            self.assertEqual(result["processed"], 1)
