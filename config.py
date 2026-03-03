import os
import sys

REQUIRED_VARS = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "GOOGLE_SHEET_ID"]

_missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
if _missing:
    print(f"Missing required environment variables: {', '.join(_missing)}", file=sys.stderr)
    raise SystemExit(1)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
