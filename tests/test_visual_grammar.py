import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from visual_dialogue_corpus.visual_grammar import measure


class VisualGrammarTests(unittest.TestCase):
    def test_measures_right_edge_contact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "edge.png"
            image = Image.new("RGB", (128, 128), "white")
            ImageDraw.Draw(image).line((30, 64, 127, 64), fill="black", width=6)
            image.save(path)
            result = measure(path)
        self.assertTrue(result["touch_right"])
        self.assertFalse(result["touch_left"])
