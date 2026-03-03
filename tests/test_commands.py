from bot.commands import parse_command, Command


class TestCreateCommand:
    def test_create_task_without_assignee(self):
        result = parse_command("create task Fix login bug")
        assert result == Command("create", {"name": "Fix login bug", "assignee": None})

    def test_create_task_with_assignee(self):
        result = parse_command("create task Fix bug assign to <@U123>")
        assert result == Command("create", {"name": "Fix bug", "assignee": "U123"})


class TestListCommand:
    def test_list_tasks(self):
        result = parse_command("list tasks")
        assert result == Command("list", {"status_filter": None})

    def test_what_tasks_are_open(self):
        result = parse_command("what tasks are open?")
        assert result == Command("list", {"status_filter": "open"})


class TestUpdateStatusCommand:
    def test_update_task_status(self):
        result = parse_command("update task 3 status to done")
        assert result == Command("update_status", {"task_id": "3", "status": "done"})


class TestGetStatusCommand:
    def test_status_of_task(self):
        result = parse_command("status of task 5")
        assert result == Command("get_status", {"task_id": "5"})


class TestWhoAssignedCommand:
    def test_who_is_assigned(self):
        result = parse_command("who is assigned to task 5?")
        assert result == Command("who_assigned", {"task_id": "5"})


class TestAssignCommand:
    def test_assign_task(self):
        result = parse_command("assign task 2 to <@U456>")
        assert result == Command("assign", {"task_id": "2", "assignee": "U456"})


class TestHelpCommand:
    def test_help(self):
        result = parse_command("help")
        assert result == Command("help", {})


class TestUnknownCommand:
    def test_unknown_text(self):
        result = parse_command("gibberish")
        assert result == Command("unknown", {"text": "gibberish"})
