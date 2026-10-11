import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "botsee", Path(__file__).resolve().parents[1] / "skills/botsee/botsee.py"
)
botsee = importlib.util.module_from_spec(spec)
spec.loader.exec_module(botsee)


class UpdateSiteTest(unittest.TestCase):
    def run_command(self, flags, response=({"site": {}}, 200), expected_exit=None):
        with patch.object(sys, "argv", ["botsee", "update-site", "site-uuid", *flags]), \
                patch.object(botsee, "require_user_config", return_value={"api_key": "test"}), \
                patch.object(botsee, "api_call", return_value=response) as api, \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            if expected_exit is None:
                botsee.main()
            else:
                with self.assertRaises(SystemExit) as raised:
                    botsee.main()
                self.assertEqual(raised.exception.code, expected_exit)
        return api

    def test_partial_update_omits_unspecified_fields(self):
        api = self.run_command(["--aliases", "Acme, Acme Points"])
        api.assert_called_once_with(
            "PUT", "/sites/site-uuid", data={"aliases": "Acme, Acme Points"}, api_key="test"
        )

    def test_all_metadata_flags_reach_api(self):
        api = self.run_command([
            "--aliases", "Acme", "--product-name", "New name",
            "--value-proposition", "New description",
        ])
        self.assertEqual(api.call_args.kwargs["data"], {
            "aliases": "Acme", "product_name": "New name",
            "value_proposition": "New description",
        })

    def test_empty_aliases_are_sent(self):
        api = self.run_command(["--aliases", ""])
        self.assertEqual(api.call_args.kwargs["data"], {"aliases": ""})

    def test_missing_flags_stop_before_api_call(self):
        api = self.run_command([], expected_exit=1)
        api.assert_not_called()

    def test_api_error_exits_unsuccessfully(self):
        api = self.run_command(["--aliases", "Acme"], ({"error": "Not found"}, 404), 1)
        api.assert_called_once()


if __name__ == "__main__":
    unittest.main()
