import unittest

from visual_dialogue_corpus.dada import ConversationParser, _public_conversation_url


class DadaTests(unittest.TestCase):
    def test_parses_public_turn(self) -> None:
        parser = ConversationParser()
        parser.feed('<article class="replies root" data-activity="133"><img src="https://img/x.png"><a href="/portraits/serste"><h4>Serste</h4></a></article>')
        self.assertEqual(parser.turns[0]["activity_id"], "133")
        self.assertEqual(parser.turns[0]["author_id"], "serste")
        self.assertEqual(parser.turns[0]["image_url"], "https://img/x.png")

    def test_restricts_seed_host_and_shape(self) -> None:
        self.assertEqual(_public_conversation_url("133752")[1], "133752")
        with self.assertRaises(ValueError):
            _public_conversation_url("https://example.com/pa/133752")

    def test_collect_parser_preserves_rendered_order(self) -> None:
        parser = ConversationParser()
        parser.feed('<article data-activity="1"><img src="https://img/1.png"><h4>A</h4></article><article data-activity="2"><img src="https://img/2.png"><h4>B</h4></article>')
        self.assertEqual([turn["activity_id"] for turn in parser.turns], ["1", "2"])
