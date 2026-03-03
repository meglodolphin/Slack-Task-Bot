import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

from bot.app import create_app

logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Slack Task Bot...")
    app, handler = create_app()
    handler.start()


if __name__ == "__main__":
    main()
