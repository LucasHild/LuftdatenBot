#!/usr/bin/python3
# luftdaten-telegram.py

import modules
import config
from telegram.ext import Updater
import logging
import os


updater = Updater(token=config.bottoken)

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename=os.path.dirname(os.path.realpath(__file__)) + "/logs/luftdaten-telegram.log")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Started luftdaten-telegram.py")

    users = modules.get_users_not_sent()
    for user in users:
        sensor_id = user[1]
        chat_id = user[2]
        limitation = user[3]

        # Get value
        value = int(modules.get_value(str(sensor_id)))

        # Send value if necessary
        if int(value) > int(limitation):
            updater.bot.send_message(chat_id=int(chat_id),
                                     text="Achtung: Dein Feinstaubsensor hat " + str(value) + " Partikel pro m3 gemessen.")
            logger.info("Sent message to " + str(chat_id))
            modules.add_message_to_sent_message(chat_id)

    logger.info("Finished luftdaten-telegram.py")
