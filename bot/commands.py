import re
from typing import NamedTuple


class Command(NamedTuple):
    action: str
    params: dict


PATTERNS = [
    (
        re.compile(r"create\s+task\s+(.+?)\s+assign\s+to\s+<@(\w+)>", re.IGNORECASE),
        lambda m: Command("create", {"name": m.group(1).strip(), "assignee": m.group(2)}),
    ),
    (
        re.compile(r"create\s+task\s+(.+)", re.IGNORECASE),
        lambda m: Command("create", {"name": m.group(1).strip(), "assignee": None}),
    ),
    (
        re.compile(r"what\s+tasks\s+are\s+(\w+)", re.IGNORECASE),
        lambda m: Command("list", {"status_filter": m.group(1).rstrip("?")}),
    ),
    (
        re.compile(r"list\s+tasks", re.IGNORECASE),
        lambda m: Command("list", {"status_filter": None}),
    ),
    (
        re.compile(r"update\s+task\s+(\d+)\s+status\s+to\s+(\w+)", re.IGNORECASE),
        lambda m: Command("update_status", {"task_id": m.group(1), "status": m.group(2)}),
    ),
    (
        re.compile(r"status\s+of\s+task\s+(\d+)", re.IGNORECASE),
        lambda m: Command("get_status", {"task_id": m.group(1)}),
    ),
    (
        re.compile(r"who\s+is\s+assigned\s+to\s+task\s+(\d+)", re.IGNORECASE),
        lambda m: Command("who_assigned", {"task_id": m.group(1).rstrip("?")}),
    ),
    (
        re.compile(r"assign\s+task\s+(\d+)\s+to\s+<@(\w+)>", re.IGNORECASE),
        lambda m: Command("assign", {"task_id": m.group(1), "assignee": m.group(2)}),
    ),
    (
        re.compile(r"help", re.IGNORECASE),
        lambda m: Command("help", {}),
    ),
]


def parse_command(text: str) -> Command:
    text = text.strip()
    for pattern, handler in PATTERNS:
        match = pattern.search(text)
        if match:
            return handler(match)
    return Command("unknown", {"text": text})
