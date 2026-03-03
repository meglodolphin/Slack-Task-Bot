import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import config
from bot.sheets import SheetsClient
from bot.handlers import handle_mention

logger = logging.getLogger(__name__)


def create_app() -> tuple[App, SocketModeHandler]:
    app = App(token=config.SLACK_BOT_TOKEN)
    sheets = SheetsClient(sheet_id=config.GOOGLE_SHEET_ID)

    auth_response = app.client.auth_test()
    bot_id = auth_response["user_id"]
    logger.info("Bot user ID: %s", bot_id)

    @app.event("app_mention")
    def on_mention(event, say):
        logger.info("Mention received: %s", event.get("text", ""))
        handle_mention(event, say, app.client, sheets, bot_id=bot_id)

    handler = SocketModeHandler(app, config.SLACK_APP_TOKEN)
    return app, handler
