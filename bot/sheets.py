from datetime import date

import gspread


class SheetError(Exception):
    pass


HEADERS = [
    "Task ID", "Task Name", "Description", "Assignee", "Status",
    "Priority", "Due Date", "Created Date", "Updated Date", "Channel", "Notes",
]


class SheetsClient:
    def __init__(self, sheet_id: str, creds_path: str = "service_account.json"):
        gc = gspread.service_account(filename=creds_path)
        spreadsheet = gc.open_by_key(sheet_id)
        self.worksheet = spreadsheet.sheet1

    def _next_id(self) -> int:
        records = self.worksheet.get_all_records()
        if not records:
            return 1
        return max(r["Task ID"] for r in records) + 1

    def create_task(
        self,
        name: str,
        assignee: str = "",
        channel: str = "",
        description: str = "",
        priority: str = "",
        due_date: str = "",
    ) -> dict:
        task_id = self._next_id()
        today = date.today().isoformat()
        row = [
            task_id, name, description, assignee, "open",
            priority, due_date, today, today, channel, "",
        ]
        self.worksheet.append_row(row)
        return {
            "id": task_id,
            "name": name,
            "assignee": assignee,
            "status": "open",
            "channel": channel,
        }

    def list_tasks(self, status_filter: str | None = None) -> list[dict]:
        records = self.worksheet.get_all_records()
        if status_filter:
            records = [r for r in records if r["Status"].lower() == status_filter.lower()]
        return records

    def get_task(self, task_id: str) -> dict | None:
        records = self.worksheet.get_all_records()
        for r in records:
            if str(r["Task ID"]) == str(task_id):
                return r
        return None

    def _find_row(self, task_id: str) -> int:
        task = self.get_task(task_id)
        if task is None:
            raise SheetError(f"Task {task_id} not found")
        cell = self.worksheet.find(str(task["Task ID"]))
        return cell.row

    def update_task_status(self, task_id: str, status: str) -> None:
        row = self._find_row(task_id)
        self.worksheet.update_cell(row, 5, status)  # Status = col 5
        self.worksheet.update_cell(row, 9, date.today().isoformat())  # Updated Date = col 9

    def assign_task(self, task_id: str, assignee: str) -> None:
        row = self._find_row(task_id)
        self.worksheet.update_cell(row, 4, assignee)  # Assignee = col 4
        self.worksheet.update_cell(row, 9, date.today().isoformat())  # Updated Date = col 9
