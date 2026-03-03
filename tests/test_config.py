import os
from unittest.mock import patch

import pytest


class TestConfig:
    def test_missing_slack_bot_token_raises_system_exit(self):
        env = {
            "SLACK_APP_TOKEN": "xapp-test",
            "GOOGLE_SHEET_ID": "sheet-id",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(SystemExit):
                import importlib
                import config
                importlib.reload(config)

    def test_missing_slack_app_token_raises_system_exit(self):
        env = {
            "SLACK_BOT_TOKEN": "xoxb-test",
            "GOOGLE_SHEET_ID": "sheet-id",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(SystemExit):
                import importlib
                import config
                importlib.reload(config)

    def test_missing_google_sheet_id_raises_system_exit(self):
        env = {
            "SLACK_BOT_TOKEN": "xoxb-test",
            "SLACK_APP_TOKEN": "xapp-test",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(SystemExit):
                import importlib
                import config
                importlib.reload(config)

    def test_all_vars_present_exposes_constants(self):
        env = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_APP_TOKEN": "xapp-test-token",
            "GOOGLE_SHEET_ID": "test-sheet-id",
        }
        with patch.dict(os.environ, env, clear=True):
            import importlib
            import config
            importlib.reload(config)
            assert config.SLACK_BOT_TOKEN == "xoxb-test-token"
            assert config.SLACK_APP_TOKEN == "xapp-test-token"
            assert config.GOOGLE_SHEET_ID == "test-sheet-id"
