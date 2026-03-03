def task_created(task: dict) -> str:
    assignee = task.get("assignee") or "unassigned"
    return f"*Task #{task['id']} created:* {task['name']}\nAssigned to: {assignee}"


def task_list(tasks: list[dict]) -> str:
    if not tasks:
        return "No tasks found."
    lines = []
    for t in tasks:
        lines.append(f"*#{t['Task ID']}* {t['Task Name']} [{t['Status']}] - {t.get('Assignee', 'unassigned')}")
    return "\n".join(lines)


def task_status(task: dict) -> str:
    return f"*Task #{task['Task ID']}* ({task['Task Name']}): status is *{task['Status']}*"


def task_assignee(task: dict) -> str:
    assignee = task.get("Assignee") or "unassigned"
    return f"*Task #{task['Task ID']}* ({task['Task Name']}) is assigned to *{assignee}*"


def task_updated(task_id: str, status: str) -> str:
    return f"Task #{task_id} status updated to *{status}*"


def task_assigned(task_id: str, assignee: str) -> str:
    return f"Task #{task_id} assigned to *{assignee}*"


def help_message() -> str:
    return (
        "*Available commands:*\n"
        "- `create task <name> [assign to @user]` - Create a new task\n"
        "- `list tasks` / `what tasks are <status>?` - List tasks\n"
        "- `update task <id> status to <status>` - Update task status\n"
        "- `status of task <id>` - Get task status\n"
        "- `who is assigned to task <id>?` - Check assignee\n"
        "- `assign task <id> to @user` - Assign a task\n"
        "- `help` - Show this message"
    )


def unknown_command(text: str) -> str:
    return f"I didn't understand: _{text}_\nType `help` to see available commands."


def error_message(msg: str) -> str:
    return f":warning: {msg}"
