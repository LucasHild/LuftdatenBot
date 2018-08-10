import logging
from functools import wraps

from bot import sentry_client

logger = logging.getLogger(__name__)


def catch_error(f):
    """Function runs before handling a request"""
    @wraps(f)
    def wrap(bot, update):
        chat_id = update.message.chat_id
        username = update.message.from_user.username

        logger.info(f"User {username} sent {update.message.text}")

        try:
            return f(bot, update)
        except Exception as e:
            sentry_client.user_context({
                "username": update.message.from_user.username,
                "message": update.message.text
            })

            sentry_client.captureException()
            logger.error(e, exc_info=True)
            bot.send_message(
                chat_id=chat_id,
                text="Ein Fehler ist aufgetreten! Ich kümmere mich darum ..."
            )

            sentry_client.context.clear()

    return wrap


def error_callback(bot, update, error):
    try:
        raise error
    except Exception as e:
        logger.error(str(e))
        sentry_client.captureException()
