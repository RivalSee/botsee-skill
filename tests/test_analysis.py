import contextlib
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "botsee", Path(__file__).resolve().parents[1] / "skills/botsee/botsee.py"
)
botsee = importlib.util.module_from_spec(spec)
spec.loader.exec_module(botsee)


class AnalysisTest(unittest.TestCase):
    def run_analysis(self, responses, dry_run=False, no_persona=False):
        args = SimpleNamespace(
            site_uuid="site", scope="site", models="claude",
            dry_run=dry_run, no_persona=no_persona,
        )
        output = io.StringIO()
        with patch.object(botsee, "require_user_config", return_value={"api_key": "test"}), \
                patch.object(botsee, "api_call", side_effect=responses) as api, \
                patch.object(botsee.time, "sleep"), contextlib.redirect_stdout(output):
            botsee.cmd_analyze(args)
        return api, output.getvalue()

    def preview(self):
        return {"preview": {
            "estimated_credit_range": {"min": 20, "max": 32},
            "warnings": [{"code": "brand_terms", "question_uuid": "q", "terms": ["acme"]}],
        }}, 200

    def test_dry_run_previews_without_starting_or_polling(self):
        api, output = self.run_analysis([self.preview()], dry_run=True)
        self.assertEqual(api.call_count, 1)
        self.assertTrue(api.call_args.kwargs["data"]["dry_run"])
        self.assertTrue(api.call_args.kwargs["data"]["include_persona"])
        self.assertIn("20–32", output)
        self.assertIn("acme", output)
        self.assertIn("snapshot", output)

    def test_persona_opt_out_reaches_preview_and_run(self):
        responses = [self.preview(), ({"analysis": {"uuid": "run"}}, 202),
                     ({"analysis": {"status": "completed"}}, 200)] + [({}, 200)] * 4
        api, _ = self.run_analysis(responses, no_persona=True)
        preview, start = api.call_args_list[:2]
        self.assertFalse(preview.kwargs["data"]["include_persona"])
        self.assertFalse(start.kwargs["data"]["include_persona"])
        self.assertNotIn("dry_run", start.kwargs["data"])

    def test_failed_preview_stops_before_paid_run(self):
        with patch.object(botsee, "require_user_config", return_value={"api_key": "test"}), \
                patch.object(botsee, "api_call", return_value=({}, 400)) as api, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            args = SimpleNamespace(site_uuid="site", scope=None, models=None,
                                   no_persona=False, dry_run=False)
            with self.assertRaises(SystemExit):
                botsee.cmd_analyze(args)
            self.assertEqual(api.call_count, 1)


if __name__ == "__main__":
    unittest.main()
