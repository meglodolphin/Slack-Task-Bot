from unittest.mock import patch, MagicMock
from datetime import date

import pytest

from bot.sheets import SheetsClient, SheetError


class TestCreateTask:
    def setup_method(self):
        self.mock_worksheet = MagicMock()
        self.mock_worksheet.get_all_records.return_value = []
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.sheet1 = self.mock_worksheet

        with patch("bot.sheets.gspread.service_account") as mock_sa:
            mock_sa.return_value.open_by_key.return_value = mock_spreadsheet
            self.client = SheetsClient(
                sheet_id="test-sheet-id",
                creds_path="fake-creds.json",
            )

    def test_create_task_appends_row_and_returns_dict(self):
        self.mock_worksheet.get_all_records.return_value = []

        result = self.client.create_task(
            name="Fix login bug",
            assignee="Joel",
            channel="C123",
        )

        self.mock_worksheet.append_row.assert_called_once()
        row = self.mock_worksheet.append_row.call_args[0][0]
        assert row[0] == 1  # Task ID
        assert row[1] == "Fix login bug"  # Task Name
        assert row[3] == "Joel"  # Assignee
        assert row[4] == "open"  # Status
        assert row[9] == "C123"  # Channel

        assert result["id"] == 1
        assert result["name"] == "Fix login bug"
        assert result["assignee"] == "Joel"
        assert result["status"] == "open"

    def test_create_task_increments_id(self):
        self.mock_worksheet.get_all_records.return_value = [
            {"Task ID": 1, "Task Name": "Existing"},
            {"Task ID": 2, "Task Name": "Another"},
        ]

        result = self.client.create_task(name="New task", channel="C123")

        row = self.mock_worksheet.append_row.call_args[0][0]
        assert row[0] == 3
        assert result["id"] == 3


SAMPLE_RECORDS = [
    {"Task ID": 1, "Task Name": "Bug fix", "Assignee": "Joel", "Status": "open", "Channel": "C1"},
    {"Task ID": 2, "Task Name": "Feature", "Assignee": "Sarah", "Status": "done", "Channel": "C1"},
    {"Task ID": 3, "Task Name": "Refactor", "Assignee": "Joel", "Status": "open", "Channel": "C2"},
]


class TestListTasks:
    def setup_method(self):
        self.mock_worksheet = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.sheet1 = self.mock_worksheet

        with patch("bot.sheets.gspread.service_account") as mock_sa:
            mock_sa.return_value.open_by_key.return_value = mock_spreadsheet
            self.client = SheetsClient(sheet_id="test", creds_path="fake.json")

    def test_list_all_tasks(self):
        self.mock_worksheet.get_all_records.return_value = SAMPLE_RECORDS
        result = self.client.list_tasks()
        assert len(result) == 3

    def test_list_tasks_with_status_filter(self):
        self.mock_worksheet.get_all_records.return_value = SAMPLE_RECORDS
        result = self.client.list_tasks(status_filter="open")
        assert len(result) == 2
        assert all(r["Status"] == "open" for r in result)


class TestGetTask:
    def setup_method(self):
        self.mock_worksheet = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.sheet1 = self.mock_worksheet

        with patch("bot.sheets.gspread.service_account") as mock_sa:
            mock_sa.return_value.open_by_key.return_value = mock_spreadsheet
            self.client = SheetsClient(sheet_id="test", creds_path="fake.json")

    def test_get_existing_task(self):
        self.mock_worksheet.get_all_records.return_value = SAMPLE_RECORDS
        result = self.client.get_task("3")
        assert result["Task ID"] == 3
        assert result["Task Name"] == "Refactor"

    def test_get_nonexistent_task_returns_none(self):
        self.mock_worksheet.get_all_records.return_value = SAMPLE_RECORDS
        result = self.client.get_task("999")
        assert result is None


class TestUpdateTaskStatus:
    def setup_method(self):
        self.mock_worksheet = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.sheet1 = self.mock_worksheet

        with patch("bot.sheets.gspread.service_account") as mock_sa:
            mock_sa.return_value.open_by_key.return_value = mock_spreadsheet
            self.client = SheetsClient(sheet_id="test", creds_path="fake.json")

    def test_update_status_calls_update_cell(self):
        self.mock_worksheet.get_all_records.return_value = SAMPLE_RECORDS
        # find_task returns row 2 (1-indexed header + 1-indexed data row)
        # Task ID 3 is at index 2 in records (0-based), so sheet row = 2 + 1 + 1 = 4
        self.mock_worksheet.find.return_value = MagicMock(row=4)

        self.client.update_task_status("3", "done")

        # Status is column 5 (E), Updated Date is column 9 (I)
        self.mock_worksheet.update_cell.assert_any_call(4, 5, "done")
        self.mock_worksheet.update_cell.assert_any_call(4, 9, date.today().isoformat())

    def test_update_nonexistent_task_raises_sheet_error(self):
        self.mock_worksheet.get_all_records.return_value = SAMPLE_RECORDS

        with pytest.raises(SheetError):
            self.client.update_task_status("999", "done")


class TestAssignTask:
    def setup_method(self):
        self.mock_worksheet = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.sheet1 = self.mock_worksheet

        with patch("bot.sheets.gspread.service_account") as mock_sa:
            mock_sa.return_value.open_by_key.return_value = mock_spreadsheet
            self.client = SheetsClient(sheet_id="test", creds_path="fake.json")

    def test_assign_task_updates_assignee_cell(self):
        self.mock_worksheet.get_all_records.return_value = SAMPLE_RECORDS
        self.mock_worksheet.find.return_value = MagicMock(row=3)

        self.client.assign_task("2", "Sarah")

        # Assignee is column 4 (D), Updated Date is column 9 (I)
        self.mock_worksheet.update_cell.assert_any_call(3, 4, "Sarah")
        self.mock_worksheet.update_cell.assert_any_call(3, 9, date.today().isoformat())
