"""Tests for bin/sensation.py — Korzybski IS detection and XML tagging."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure bin/ is on the import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))

from sensation import (
    classify_statement,
    detect_is_type,
    is_subjective,
    preprocess_conversation,
    preprocess_corpus,
    preprocess_training_example,
    tag_message,
)


# =====================================================================
#  Korzybski IS detection
# =====================================================================


class TestDetectIsType(unittest.TestCase):
    """Test the IS-pattern subtype detector."""

    def test_identity(self):
        self.assertEqual(detect_is_type("Socrates is a man"), "identity")

    def test_identity_plural(self):
        self.assertEqual(detect_is_type("Dogs are animals"), "identity")

    def test_identity_the(self):
        self.assertEqual(detect_is_type("Paris is the capital of France"), "identity")

    def test_existence(self):
        self.assertEqual(detect_is_type("There are eight planets"), "existence")

    def test_existence_singular(self):
        self.assertEqual(detect_is_type("There is a bug in the code"), "existence")

    def test_mereological(self):
        self.assertEqual(detect_is_type("Water contains hydrogen"), "mereological")

    def test_mereological_part_of(self):
        self.assertEqual(detect_is_type("The engine is part of the car"), "mereological")

    def test_quantity(self):
        self.assertEqual(detect_is_type("I have 3 cats"), "quantity")

    def test_definition(self):
        self.assertEqual(detect_is_type("A polygon is defined as a closed shape"), "definition")

    def test_definition_known_as(self):
        self.assertEqual(detect_is_type("It is known as the Big Apple"), "definition")

    def test_no_is_pattern(self):
        self.assertIsNone(detect_is_type("Hello there"))

    def test_no_is_greeting(self):
        self.assertIsNone(detect_is_type("Good morning"))


class TestIsSubjective(unittest.TestCase):
    """Test hedging / subjective marker detection."""

    def test_i_think(self):
        self.assertTrue(is_subjective("I think this is correct"))

    def test_i_feel(self):
        self.assertTrue(is_subjective("I feel that we should go"))

    def test_maybe(self):
        self.assertTrue(is_subjective("Maybe it will rain tomorrow"))

    def test_probably(self):
        self.assertTrue(is_subjective("It will probably work"))

    def test_might_be(self):
        self.assertTrue(is_subjective("It might be useful"))

    def test_in_my_opinion(self):
        self.assertTrue(is_subjective("In my opinion this is wrong"))

    def test_factual_not_subjective(self):
        self.assertFalse(is_subjective("Paris is the capital of France"))

    def test_plain_statement(self):
        self.assertFalse(is_subjective("The train departs at 9 AM"))


class TestClassifyStatement(unittest.TestCase):
    """Test the top-level classifier."""

    def test_fact_identity(self):
        tag, subtype = classify_statement("Paris is the capital of France.")
        self.assertEqual(tag, "fact")
        self.assertEqual(subtype, "identity")

    def test_fact_existence(self):
        tag, subtype = classify_statement("There are 50 states in the US.")
        self.assertEqual(tag, "fact")
        self.assertEqual(subtype, "existence")

    def test_feeling_question(self):
        tag, subtype = classify_statement("Is Paris the capital?")
        self.assertEqual(tag, "feeling")
        self.assertIsNone(subtype)

    def test_feeling_subjective(self):
        tag, subtype = classify_statement("I think Paris is beautiful.")
        self.assertEqual(tag, "feeling")
        self.assertIsNone(subtype)

    def test_feeling_meta_discourse(self):
        tag, subtype = classify_statement("That's a great question!")
        self.assertEqual(tag, "feeling")
        self.assertIsNone(subtype)

    def test_feeling_empty(self):
        tag, subtype = classify_statement("")
        self.assertEqual(tag, "feeling")
        self.assertIsNone(subtype)

    def test_feeling_greeting(self):
        tag, subtype = classify_statement("Hello there, how are you?")
        self.assertEqual(tag, "feeling")
        self.assertIsNone(subtype)

    def test_fact_mereological(self):
        tag, subtype = classify_statement("Water contains hydrogen and oxygen.")
        self.assertEqual(tag, "fact")
        self.assertEqual(subtype, "mereological")

    def test_feeling_hedged_is(self):
        """Hedged claim: 'might be' overrides IS detection."""
        tag, _ = classify_statement("It might be the largest city.")
        self.assertEqual(tag, "feeling")


# =====================================================================
#  Tag wrapping
# =====================================================================


class TestTagMessage(unittest.TestCase):
    """Test XML tag wrapping of messages."""

    def test_user_feeling(self):
        result = tag_message("Hello!", "user")
        self.assertTrue(result.startswith("<Q>"))
        self.assertTrue(result.endswith("</Q>"))
        self.assertIn("<feeling>", result)

    def test_assistant_feeling(self):
        result = tag_message("Thanks for asking!", "assistant")
        self.assertTrue(result.startswith("<R>"))
        self.assertTrue(result.endswith("</R>"))
        self.assertIn("<feeling>", result)

    def test_fact_detected(self):
        result = tag_message("Paris is the capital of France.", "assistant")
        self.assertIn("<R>", result)
        self.assertIn("<fact", result)
        self.assertIn('trust="0.5"', result)
        self.assertIn('spacetime="[unverified]"', result)

    def test_explicit_trust_overrides(self):
        result = tag_message("Hello world", "user", trust=0.9)
        self.assertIn("<fact", result)
        self.assertIn('trust="0.9"', result)
        self.assertNotIn("<feeling>", result)

    def test_empty_content(self):
        result = tag_message("", "user")
        self.assertEqual(result, "<Q><feeling></feeling></Q>")

    def test_xml_escaping(self):
        result = tag_message('Use <div> & "quotes"', "user")
        self.assertIn("&lt;div&gt;", result)
        self.assertIn("&amp;", result)
        self.assertIn("&quot;quotes&quot;", result)

    def test_mixed_sentences(self):
        """Message with both fact and feeling sentences."""
        text = "That is great! Paris is the capital of France."
        result = tag_message(text, "assistant")
        self.assertIn("<feeling>", result)
        self.assertIn("<fact", result)


# =====================================================================
#  Conversation processing
# =====================================================================


class TestPreprocessConversation(unittest.TestCase):
    """Test conversation-level processing."""

    def test_basic_conversation(self):
        messages = [
            {"role": "user", "content": "What is Paris?"},
            {"role": "assistant", "content": "Paris is the capital of France."},
        ]
        result = preprocess_conversation(messages)

        self.assertEqual(len(result["messages"]), 2)
        self.assertIn("<Q>", result["messages"][0]["content"])
        self.assertIn("<R>", result["messages"][1]["content"])

    def test_truth_extraction(self):
        messages = [
            {"role": "user", "content": "Tell me about water."},
            {"role": "assistant", "content": "Water contains hydrogen and oxygen."},
        ]
        result = preprocess_conversation(messages, extract_truth=True)

        # "Water contains hydrogen and oxygen" should produce a fact
        self.assertGreater(len(result["truth_entries"]), 0)
        entry = result["truth_entries"][0]
        self.assertEqual(entry["type"], "truth")
        self.assertIn("trust", entry)
        self.assertIn("id", entry)

    def test_no_truth_extraction(self):
        messages = [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        result = preprocess_conversation(messages, extract_truth=True)
        # Greetings should not produce facts
        self.assertEqual(len(result["truth_entries"]), 0)

    def test_extract_truth_false(self):
        messages = [
            {"role": "assistant", "content": "Paris is the capital of France."},
        ]
        result = preprocess_conversation(messages, extract_truth=False)
        self.assertEqual(result["truth_entries"], [])


# =====================================================================
#  Training example preprocessing
# =====================================================================


class TestPreprocessTrainingExample(unittest.TestCase):
    """Test dynamic training example tagging."""

    def test_returns_tagged_messages(self):
        messages = [
            {"role": "user", "content": "What is 2+2?"},
            {"role": "assistant", "content": "The answer is 4."},
        ]
        result = preprocess_training_example(messages, degree_of_truth=0.8)
        self.assertEqual(len(result), 2)
        self.assertIn("<Q>", result[0]["content"])
        self.assertIn("<R>", result[1]["content"])

    def test_preserves_role(self):
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]
        result = preprocess_training_example(messages, degree_of_truth=1.0)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[1]["role"], "assistant")


# =====================================================================
#  Corpus batch processing
# =====================================================================


class TestPreprocessCorpus(unittest.TestCase):
    """Test JSONL corpus batch conversion."""

    def test_basic_corpus(self):
        corpus_lines = [
            json.dumps([
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi there!"},
            ]),
            json.dumps([
                {"role": "user", "content": "What is water?"},
                {"role": "assistant", "content": "Water is a molecule."},
            ]),
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as fin:
            fin.write("\n".join(corpus_lines) + "\n")
            in_path = Path(fin.name)

        out_path = in_path.with_suffix(".tagged.jsonl")
        try:
            stats = preprocess_corpus(in_path, out_path)

            self.assertEqual(stats["processed"], 2)
            self.assertEqual(stats["errors"], 0)
            self.assertGreater(stats["facts_found"], 0)

            # Verify output structure
            with out_path.open() as f:
                records = [json.loads(line) for line in f if line.strip()]

            types = [r["type"] for r in records]
            self.assertIn("user", types)
            self.assertIn("server", types)
            self.assertIn("conversation", types)
            # Should have truth entries for "Water is a molecule"
            self.assertIn("truth", types)

        finally:
            in_path.unlink(missing_ok=True)
            out_path.unlink(missing_ok=True)

    def test_malformed_line_skipped(self):
        corpus_lines = [
            "not valid json",
            json.dumps([
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
            ]),
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as fin:
            fin.write("\n".join(corpus_lines) + "\n")
            in_path = Path(fin.name)

        out_path = in_path.with_suffix(".tagged.jsonl")
        try:
            stats = preprocess_corpus(in_path, out_path)
            self.assertEqual(stats["processed"], 1)
            self.assertEqual(stats["errors"], 1)
        finally:
            in_path.unlink(missing_ok=True)
            out_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
