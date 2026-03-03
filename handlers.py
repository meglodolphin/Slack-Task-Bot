import re

from bot.commands import parse_command
from bot import formatters
from bot.sheets import SheetError


def resolve_user(client, user_id: str) -> str:
    try:
        result = client.users_info(user=user_id)
        return result["user"]["real_name"]
    except Exception:
        return user_id


def _strip_mention(text: str, bot_id: str) -> str:
    return re.sub(rf"<@{bot_id}>\s*", "", text).strip()


def handle_mention(event, say, client, sheets, bot_id: str):
    text = _strip_mention(event["text"], bot_id)
    channel = event.get("channel", "")
    command = parse_command(text)

    try:
        match command.action:
            case "create":
                assignee_name = ""
                if command.params.get("assignee"):
                    assignee_name = resolve_user(client, command.params["assignee"])
                task = sheets.create_task(
                    name=command.params["name"],
                    assignee=assignee_name,
                    channel=channel,
                )
                say(formatters.task_created(task))

            case "list":
                tasks = sheets.list_tasks(status_filter=command.params.get("status_filter"))
                say(formatters.task_list(tasks))

            case "update_status":
                sheets.update_task_status(command.params["task_id"], command.params["status"])
                say(formatters.task_updated(command.params["task_id"], command.params["status"]))

            case "get_status":
                task = sheets.get_task(command.params["task_id"])
                if task is None:
                    say(formatters.error_message(f"Task {command.params['task_id']} not found"))
                else:
                    say(formatters.task_status(task))

            case "who_assigned":
                task = sheets.get_task(command.params["task_id"])
                if task is None:
                    say(formatters.error_message(f"Task {command.params['task_id']} not found"))
                else:
                    say(formatters.task_assignee(task))

            case "assign":
                assignee_name = resolve_user(client, command.params["assignee"])
                sheets.assign_task(command.params["task_id"], assignee_name)
                say(formatters.task_assigned(command.params["task_id"], assignee_name))

            case "help":
                say(formatters.help_message())

            case "unknown":
                say(formatters.unknown_command(command.params.get("text", text)))

    except SheetError as e:
        say(formatters.error_message(str(e)))
    except Exception:
        say(formatters.error_message("Something went wrong. Please try again."))
