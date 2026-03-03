from bot.formatters import (
    task_created,
    task_list,
    task_status,
    task_assignee,
    task_updated,
    task_assigned,
    help_message,
    unknown_command,
    error_message,
)


class TestTaskCreated:
    def test_returns_mrkdwn_with_task_details(self):
        result = task_created({"id": 1, "name": "Fix bug", "assignee": "Joel"})
        assert "Fix bug" in result
        assert "1" in result
        assert "Joel" in result


class TestTaskList:
    def test_empty_list(self):
        result = task_list([])
        assert "No tasks found" in result

    def test_nonempty_list(self):
        tasks = [
            {"Task ID": 1, "Task Name": "Bug fix", "Status": "open", "Assignee": "Joel"},
            {"Task ID": 2, "Task Name": "Feature", "Status": "done", "Assignee": "Sarah"},
        ]
        result = task_list(tasks)
        assert "Bug fix" in result
        assert "Feature" in result
        assert "1" in result
        assert "2" in result


class TestTaskStatus:
    def test_shows_task_status(self):
        task = {"Task ID": 5, "Task Name": "Deploy", "Status": "in progress"}
        result = task_status(task)
        assert "5" in result
        assert "in progress" in result


class TestTaskAssignee:
    def test_shows_assignee(self):
        task = {"Task ID": 5, "Task Name": "Deploy", "Assignee": "Joel"}
        result = task_assignee(task)
        assert "Joel" in result
        assert "5" in result


class TestTaskUpdated:
    def test_status_updated(self):
        result = task_updated("3", "done")
        assert "3" in result
        assert "done" in result


class TestTaskAssigned:
    def test_assigned(self):
        result = task_assigned("2", "Sarah")
        assert "2" in result
        assert "Sarah" in result


class TestHelpMessage:
    def test_contains_commands(self):
        result = help_message()
        assert "create task" in result
        assert "list tasks" in result
        assert "update" in result
        assert "status" in result
        assert "assign" in result
        assert "help" in result


class TestUnknownCommand:
    def test_includes_text(self):
        result = unknown_command("foo bar")
        assert "foo bar" in result


class TestErrorMessage:
    def test_returns_error_string(self):
        result = error_message("something broke")
        assert "something broke" in result
