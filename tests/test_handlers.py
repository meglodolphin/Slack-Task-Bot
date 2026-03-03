from unittest.mock import MagicMock, patch

import pytest

from bot.handlers import handle_mention
from bot.sheets import SheetError


def make_event(text, bot_id="U_BOT"):
    return {"text": f"<@{bot_id}> {text}", "channel": "C123"}


class TestHandleMentionDispatch:
    def setup_method(self):
        self.mock_sheets = MagicMock()
        self.mock_say = MagicMock()
        self.mock_client = MagicMock()

    def test_strips_bot_mention_before_parsing(self):
        self.mock_sheets.create_task.return_value = {
            "id": 1, "name": "Test", "assignee": "", "status": "open",
        }
        event = make_event("create task Test")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_sheets.create_task.assert_called_once()
        assert self.mock_sheets.create_task.call_args[1]["name"] == "Test"

    def test_create_task_calls_sheets_and_say(self):
        self.mock_sheets.create_task.return_value = {
            "id": 1, "name": "Fix bug", "assignee": "Joel", "status": "open",
        }
        event = make_event("create task Fix bug assign to <@U123>")

        with patch("bot.handlers.resolve_user", return_value="Joel"):
            handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_sheets.create_task.assert_called_once()
        self.mock_say.assert_called_once()
        assert "Fix bug" in self.mock_say.call_args[0][0]


class TestHandleListCommand:
    def setup_method(self):
        self.mock_sheets = MagicMock()
        self.mock_say = MagicMock()
        self.mock_client = MagicMock()

    def test_list_tasks(self):
        self.mock_sheets.list_tasks.return_value = [
            {"Task ID": 1, "Task Name": "Bug", "Status": "open", "Assignee": "Joel"},
        ]
        event = make_event("list tasks")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_sheets.list_tasks.assert_called_once_with(status_filter=None)
        self.mock_say.assert_called_once()


class TestHandleUpdateStatus:
    def setup_method(self):
        self.mock_sheets = MagicMock()
        self.mock_say = MagicMock()
        self.mock_client = MagicMock()

    def test_update_status(self):
        event = make_event("update task 3 status to done")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_sheets.update_task_status.assert_called_once_with("3", "done")
        self.mock_say.assert_called_once()
        assert "3" in self.mock_say.call_args[0][0]
        assert "done" in self.mock_say.call_args[0][0]


class TestHandleGetStatus:
    def setup_method(self):
        self.mock_sheets = MagicMock()
        self.mock_say = MagicMock()
        self.mock_client = MagicMock()

    def test_get_status(self):
        self.mock_sheets.get_task.return_value = {
            "Task ID": 5, "Task Name": "Deploy", "Status": "in progress",
        }
        event = make_event("status of task 5")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_sheets.get_task.assert_called_once_with("5")
        self.mock_say.assert_called_once()

    def test_get_status_not_found(self):
        self.mock_sheets.get_task.return_value = None
        event = make_event("status of task 999")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_say.assert_called_once()
        assert "not found" in self.mock_say.call_args[0][0].lower()


class TestHandleWhoAssigned:
    def setup_method(self):
        self.mock_sheets = MagicMock()
        self.mock_say = MagicMock()
        self.mock_client = MagicMock()

    def test_who_assigned(self):
        self.mock_sheets.get_task.return_value = {
            "Task ID": 5, "Task Name": "Deploy", "Assignee": "Joel",
        }
        event = make_event("who is assigned to task 5?")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_say.assert_called_once()
        assert "Joel" in self.mock_say.call_args[0][0]


class TestHandleAssign:
    def setup_method(self):
        self.mock_sheets = MagicMock()
        self.mock_say = MagicMock()
        self.mock_client = MagicMock()

    def test_assign_task(self):
        event = make_event("assign task 2 to <@U456>")

        with patch("bot.handlers.resolve_user", return_value="Sarah"):
            handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_sheets.assign_task.assert_called_once_with("2", "Sarah")
        self.mock_say.assert_called_once()


class TestHandleHelp:
    def setup_method(self):
        self.mock_sheets = MagicMock()
        self.mock_say = MagicMock()
        self.mock_client = MagicMock()

    def test_help(self):
        event = make_event("help")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_say.assert_called_once()
        assert "create task" in self.mock_say.call_args[0][0]


class TestHandleUnknown:
    def setup_method(self):
        self.mock_sheets = MagicMock()
        self.mock_say = MagicMock()
        self.mock_client = MagicMock()

    def test_unknown(self):
        event = make_event("gibberish")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_say.assert_called_once()
        assert "gibberish" in self.mock_say.call_args[0][0]


class TestErrorHandling:
    def setup_method(self):
        self.mock_sheets = MagicMock()
        self.mock_say = MagicMock()
        self.mock_client = MagicMock()

    def test_sheet_error_sends_warning(self):
        self.mock_sheets.update_task_status.side_effect = SheetError("Task 999 not found")
        event = make_event("update task 999 status to done")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_say.assert_called_once()
        assert "Task 999 not found" in self.mock_say.call_args[0][0]

    def test_unexpected_error_sends_generic_message(self):
        self.mock_sheets.list_tasks.side_effect = RuntimeError("connection failed")
        event = make_event("list tasks")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_say.assert_called_once()
        response = self.mock_say.call_args[0][0]
        assert "error" in response.lower() or "wrong" in response.lower()

    def test_resolve_user_failure_falls_back_to_user_id(self):
        self.mock_sheets.create_task.return_value = {
            "id": 1, "name": "Test", "assignee": "U123", "status": "open",
        }
        self.mock_client.users_info.side_effect = Exception("API error")
        event = make_event("create task Test assign to <@U123>")

        handle_mention(event, self.mock_say, self.mock_client, self.mock_sheets, bot_id="U_BOT")

        self.mock_sheets.create_task.assert_called_once()
        # Should use raw user ID as fallback
        assert self.mock_sheets.create_task.call_args[1]["assignee"] == "U123"
