import logging
from raven import Client as RavenClient
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    JobQueue
)

import config

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=config.log_location + "/bot.log")
logger = logging.getLogger(__name__)

logger.info("Started bot")

# Setup sentry error tracking
sentry_client = RavenClient(
    config.sentry_token,
    ignore_exceptions=["TimedOut"]
)


# Conversation Handler States
START_SENSORID, START_LIMIT = range(2)

from bot import error, handlers  # noqa: E402
import bot.scheduler as scheduler  # noqa: E402


def main():
    updater = Updater(token=config.bottoken)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", handlers.start),
            CommandHandler("getvalue", handlers.getvalue),
            CommandHandler("setsensorid", handlers.setsensorid),
            CommandHandler("setlimit", handlers.setlimit),
            CommandHandler("details", handlers.details),
            CommandHandler("help", handlers.help),
            MessageHandler(Filters.location, handlers.location),
            MessageHandler(Filters.command, handlers.unknown)
        ],

        states={
            START_SENSORID: [
                MessageHandler(Filters.text,
                               handlers.start_setsensorid),
                MessageHandler(Filters.location,
                               handlers.start_setsensorid_location)
            ],
            START_LIMIT: [
                MessageHandler(Filters.text,
                               handlers.start_setlimit)
            ]
        },

        fallbacks=[CommandHandler("cancel", handlers.cancel)]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error.error_callback)

    # Add queue to check every 5 minutes for a to exceeding value
    jobs = JobQueue(updater.bot)
    jobs.run_repeating(
        scheduler.check_for_exceeds,
        300,
        context={
            "logger": logger,
            "sentry_client": sentry_client
        }
    )
    jobs.start()

    updater.start_polling()
    updater.idle()
