"""Offline unit tests; provider and dotenv imports are replaced with test doubles."""
import importlib.util
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


fake_genai = types.ModuleType("google.genai")
fake_genai.Client = MagicMock()
fake_google = types.ModuleType("google")
fake_google.genai = fake_genai
fake_dotenv = types.ModuleType("dotenv")
fake_dotenv.load_dotenv = MagicMock()
spec = importlib.util.spec_from_file_location(
    "planner_under_test", Path(__file__).resolve().parents[1] / "planner.py"
)
planner = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {
    "google": fake_google, "google.genai": fake_genai, "dotenv": fake_dotenv,
}):
    spec.loader.exec_module(planner)


class PlannerTests(unittest.TestCase):
    def setUp(self):
        fake_genai.Client.reset_mock(return_value=True, side_effect=True)
        self.research = {"status": "created", "subquestions": []}

    def test_valid_plan(self):
        result = planner.add_research_plan(self.research, [" A? ", "B?", "C?"])
        self.assertEqual(result["status"], "planned")
        self.assertEqual(result["subquestions"], ["A?", "B?", "C?"])

    def test_invalid_plans_leave_state_unchanged(self):
        cases = [None, "abc", [], ["A?"], ["A?", "B?", "C?", "D?"],
                 ["A?", " ", "C?"], ["A?", 2, "C?"], ["A?", " a? ", "C?"]]
        for case in cases:
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    planner.add_research_plan(self.research, case)
                self.assertEqual(self.research, {"status": "created", "subquestions": []})

    def test_invalid_topic_does_not_call_api(self):
        for topic in [None, "", "   ", "x" * 2001]:
            with self.subTest(topic_type=type(topic).__name__):
                with self.assertRaises(ValueError):
                    planner.generate_research_plan(topic)
        fake_genai.Client.assert_not_called()

    def test_missing_key_does_not_call_api(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                planner.generate_research_plan("CPU prediction")
        fake_genai.Client.assert_not_called()

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-placeholder-not-a-real-key"})
    def test_mocked_generation(self):
        client = fake_genai.Client.return_value.__enter__.return_value
        client.models.generate_content.return_value.text = '["A?", "B?", "C?"]'
        self.assertEqual(planner.generate_research_plan(" CPU prediction "), ["A?", "B?", "C?"])
        kwargs = client.models.generate_content.call_args.kwargs
        self.assertEqual(kwargs["model"], "gemini-3.1-flash-lite")
        self.assertEqual(kwargs["contents"], "Research topic:\nCPU prediction")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-placeholder-not-a-real-key"})
    def test_empty_or_invalid_json(self):
        client = fake_genai.Client.return_value.__enter__.return_value
        for output in [None, "", "not json"]:
            client.models.generate_content.return_value.text = output
            with self.assertRaises(ValueError):
                planner.generate_research_plan("CPU prediction")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-placeholder-not-a-real-key"})
    def test_provider_exception_propagates(self):
        client = fake_genai.Client.return_value.__enter__.return_value
        client.models.generate_content.side_effect = RuntimeError("provider unavailable")
        with self.assertRaises(RuntimeError):
            planner.generate_research_plan("CPU prediction")


if __name__ == "__main__":
    unittest.main()
