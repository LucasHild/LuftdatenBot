import location_modules
import logging
import os
from raven import Client
import requests
import sqlite3
import telegram

import config
import modules

from math import atan2, cos, radians, sin, sqrt
from functools import wraps
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from time import sleep


# Setup logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename=config.log_location + "/bot.log")
logger = logging.getLogger(__name__)

# Conversation Handler States
START_SENSORID, START_LIMIT = range(2)

# Setup sentry error tracking
client = Client(config.sentry_token)

def catch_error(f):
    """Function runs before handling a request"""
    @wraps(f)
    def wrap(bot, update):
        logger.info("User {user} sent {message}".format(user=update.message.from_user.username, message=update.message.text))
        try:
            return f(bot, update)
        except Exception as e:
            # Add info to error tracking
            client.user_context({
                "username": update.message.from_user.username,
                "message": update.message.text
            })

            client.captureException()
            logger.error(str(e))
            bot.send_message(chat_id=update.message.chat_id,
                             text="Ein Fehler ist aufgetreten! Ich kümmere mich darum ...")

    return wrap


@catch_error
def start(bot, update):
    # Check whether chat_id is already in database
    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE chat_id = ?", (int(update.message.chat_id),))
    fetched_users = c.fetchall()
    c.close()
    conn.close()

    if fetched_users != []:
        logger.info("User {user} called /start although he is already in the database".format(user=update.message.from_user.username))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Du hast schon alles eingerichtet! Falls Du deine Daten bearbeiten möchtest, wähle /setsensorid oder /setlimit.")
        return ConversationHandler.END

    logger.info("Bot welcomes user {user}".format(user=update.message.from_user.username))
    bot.send_message(chat_id=update.message.chat_id,
                     text="Herzlich Willkommen bei [Luftdaten-Notification](https://github.com/Lanseuo/Luftdaten-Notification)!")
    bot.send_message(chat_id=update.message.chat_id,
                     text="Wie lautet deine Sensor-ID? Schicke mir deine ID oder sende mir deinen Standort!")
    return START_SENSORID


@catch_error
def start_setsensorid(bot, update):
    sensor_id = update.message.text
    chat_id = update.message.chat_id

    # Check whether sensor_id is valid
    if modules.get_value(sensor_id) != False:

        # Check whether chat_id is already in database
        conn = sqlite3.connect(config.database_location)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE chat_id = ?", (int(chat_id),))
        fetched_users = c.fetchall()
        c.close()
        conn.close()

        # Save new user in db
        conn = sqlite3.connect(config.database_location)
        c = conn.cursor()
        c.execute("INSERT INTO users (sensor_id, chat_id, limitation, sent_message) VALUES (?, ?, ?, ?)",
                  (sensor_id, chat_id, "", "never"))
        conn.commit()
        c.close()
        conn.close()
        bot.send_message(chat_id=update.message.chat_id,
                         text="Deine Sensor-ID (" + sensor_id + ") wurde erfolgreich festgelegt!")
        logger.info("User {user} set sensor_id  to {sensor_id}".format(user=update.message.from_user.username, sensor_id=sensor_id))

    else:
        logger.info("User {user} registered with wrong sensor_id {sensor_id}".format(user=update.message.from_user.username, sensor_id=sensor_id))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Sensor " + sensor_id + " ist nicht verfügbar! Überprüfe deine Sensor ID und führe gebe die ID erneut ein!")
        return START_SENSORID

    bot.send_message(chat_id=update.message.chat_id,
                     text="Bei welchem Limit möchtest Du benachrichtigt werden?")
    return START_LIMIT


@catch_error
def start_setsensorid_location(bot, update):
    logger.info("User {user} sent location: {latitude} {longitude} at /start to setsensorid".format(user=update.message.from_user.username,
                                                                           latitude=str(
                                                                               update.message.location["latitude"]),
                                                                           longitude=str(
                                                                               update.message.location["longitude"])))

    chat_id = update.message.chat_id

    # Get position from message
    search_lat = update.message.location["latitude"]
    search_lon = update.message.location["longitude"]
    search_pos = (search_lat, search_lon)

    # Get location and id of sensors from API
    r = requests.get("https://api.luftdaten.info/static/v2/data.dust.min.json")
    sensors = r.json()

    # Get the sensor with the smallest distance to search_pos
    closest_sensor, closest_sensor_pos = location_modules.closest_sensor(search_pos, sensors)

    # Calculate distance between sensor_pos and closest_sensor
    distance = location_modules.distance(search_pos, closest_sensor_pos)

    # Send response to user
    bot.send_location(chat_id=update.message.chat_id, latitude=closest_sensor_pos[0], longitude=closest_sensor_pos[1])
    response = """
Dieser Sensor wurde als dein Hauptsensor eingerichtet:

Nächster Sensor: {closest_sensor}
Entfernung: {distance}
Messung: {value} Partikel pro m3
    """.format(closest_sensor=str(closest_sensor), distance=distance, value=str(modules.get_value(closest_sensor)))
    bot.send_message(chat_id=update.message.chat_id,
                     text=response)

    sensor_id = closest_sensor

    # Check whether chat_id is already in database
    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE chat_id = ?", (int(chat_id),))
    fetched_users = c.fetchall()
    c.close()
    conn.close()

    # Save new user in db
    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()
    c.execute("INSERT INTO users (sensor_id, chat_id, limitation, sent_message) VALUES (?, ?, ?, ?)",
              (sensor_id, chat_id, "", "never"))
    conn.commit()
    c.close()
    conn.close()

    logger.info("User {user} set sensor_id {sensor_id} with location at /start".format(user=update.message.from_user.username, sensor_id=sensor_id))

    bot.send_message(chat_id=update.message.chat_id,
                     text="Bei welchem Limit möchtest Du benachrichtigt werden?")
    return START_LIMIT


@catch_error
def start_setlimit(bot, update):
    limitation = update.message.text
    chat_id = update.message.chat_id

    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()
    c.execute("UPDATE users SET limitation = (?) WHERE chat_id = (?)", (limitation, chat_id))
    conn.commit()
    c.close()
    conn.close()
    bot.send_message(chat_id=update.message.chat_id,
                     text="Dein Limit (" + limitation + "), bei dem Du benachrichtigt wirst, wurde erfolgreich geändert!")
    logger.info("User {user} set limit to {limit} with /start".format(user=update.message.from_user.username, limit=limitation))

    return ConversationHandler.END


@catch_error
def setsensorid(bot, update):
    try:
        sensor_id = update.message.text.split(" ")[1]
    except IndexError:
        # Only command given (no value)
        logger.info("User {user} called /setsensorid without value")
        bot.send_message(chat_id=update.message.chat_id,
                         text="Du musst einen Wert angeben! Beispiel: /setsensorid 000")
        return ConversationHandler.END

    chat_id = update.message.chat_id

    # Check whether sensor_id is valid
    if modules.get_value(sensor_id) != False:

        # Check whether chat_id is already in database
        conn = sqlite3.connect(config.database_location)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE chat_id = ?", (int(chat_id),))
        fetched_users = c.fetchall()
        c.close()
        conn.close()

        # User didn't already /start
        if fetched_users == []:
            logger.info("User {user} called /setsensorid not being in the database".format(user=update.message.from_user.username))
            bot.send_message(chat_id=update.message.chat_id, text="Richte mich erst einmal mit /start ein!")
            return ConversationHandler.END

        conn = sqlite3.connect(config.database_location)
        c = conn.cursor()
        c.execute("UPDATE users SET sensor_id = (?) WHERE chat_id = (?)", (sensor_id, chat_id))
        conn.commit()
        c.close()
        conn.close()
        bot.send_message(chat_id=update.message.chat_id,
                         text="Deine Sensor-ID (" + sensor_id + ") wurde erfolgreich verändert!")
        logger.info("User {user} updated sensor_id to {sensor_id} with /setsensorid".format(user=update.message.from_user.username,
                                                                          sensor_id=sensor_id))

    else:
        logger.info("User {user} registered with wrong sensor_id {sensor_id}".format(user=update.message.from_user.username, sensor_id=sensor_id))
        bot.send_message(chat_id=update.message.chat_id, text="Sensor " + sensor_id + " ist nicht verfügbar! Überprüfe deine Sensor ID und führe den Befehl erneut aus!")

    return ConversationHandler.END


@catch_error
def setlimit(bot, update):
    try:
        limitation = update.message.text.split(" ")[1]
    except IndexError:
        # Only command given (no value)
        logger.info("User {user} called /setlimit without value".format(user=update.message.from_user.username))
        bot.send_message(chat_id=update.message.chat_id,
                         text="Du musst einen Wert angeben! Beispiel: /setlimit 50")
        return ConversationHandler.END

    chat_id = update.message.chat_id

    # Check whether chat_id is already in database
    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE chat_id = ?", (int(chat_id),))
    fetched_users = c.fetchall()
    c.close()
    conn.close()

    if fetched_users == []:
        logger.info("User {user} called /setlimit not being in the database".format(user=update.message.from_user.username))
        bot.send_message(chat_id=update.message.chat_id, text="Richte mich erst einmal mit /start ein!")
        return ConversationHandler.END

    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()
    c.execute("UPDATE users SET limitation = (?) WHERE chat_id = (?)", (limitation, chat_id))
    conn.commit()
    c.close()
    conn.close()
    bot.send_message(chat_id=update.message.chat_id,
                     text="Dein Limit (" + limitation + "), bei dem Du benachrichtigt wirst, wurde erfolgreich geändert!")
    logger.info("User {user} set limit to {limit} with /setlimit".format(user=update.message.from_user.username, limit=limitation))

    return ConversationHandler.END


@catch_error
def getvalue(bot, update):
    chat_id = update.message.chat_id

    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE chat_id = ?", (int(chat_id),))
    fetched_users = c.fetchall()
    c.close()
    conn.close()

    if fetched_users != []:
        sensor_id = fetched_users[0][1]
        value = modules.get_value(sensor_id)
        bot.send_message(chat_id=update.message.chat_id, text="Aktuell misst dein Feinstaub-Sensor *" + str(value) + " Partikel* pro m3.", parse_mode=telegram.ParseMode.MARKDOWN)
        logger.info("User {user} called /getvalue".format(user=update.message.from_user.username))

    else:
        logger.info("User {user} called /getvalue not being in the database".format(user=update.message.from_user.username))
        bot.send_message(chat_id=update.message.chat_id, text="Du musst mich zuerst mit /start einrichten!")

    return ConversationHandler.END


@catch_error
def details(bot, update):
    chat_id = update.message.chat_id
    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE chat_id = ?", (int(chat_id),))
    fetched_users = c.fetchall()
    c.close()
    conn.close()

    # User didn't already /start
    if fetched_users == []:
        logger.info(
            "User {user} called /setsensorid not being in the database".format(user=update.message.from_user.username))
        bot.send_message(chat_id=update.message.chat_id, text="Richte mich erst einmal mit /start ein!")
        return ConversationHandler.END

    user = fetched_users[0]
    value = modules.get_value(user[1])

    bot.send_message(chat_id=update.message.chat_id,
                     text="Sensor-ID: " + str(user[1]) + "\n" +
                     "Chat-ID: " + str(update.message.chat_id) + "\n" +
                     "Limit: " + str(user[3]) + "\n" +
                     "Messung: " + str(value) + " Partikel pro m3")
    return ConversationHandler.END


@catch_error
def location(bot, update):
    logger.info("User {user} sent location: {latitude} {longitude}".format(user=update.message.from_user.username,
                                                                           latitude=str(update.message.location["latitude"]),
                                                                           longitude=str(update.message.location["longitude"])))
    # Get position from message
    search_lat = update.message.location["latitude"]
    search_lon = update.message.location["longitude"]
    search_pos = (search_lat, search_lon)

    # Get location and id of sensors from API
    r = requests.get("https://api.luftdaten.info/static/v2/data.dust.min.json")
    sensors = r.json()

    # Get the sensor with the smallest distance to search_pos
    closest_sensor, closest_sensor_pos = location_modules.closest_sensor(search_pos, sensors)

    # Calculate distance between sensor_pos and closest_sensor
    distance = location_modules.distance(search_pos, closest_sensor_pos)

    # Send response to user
    bot.send_location(chat_id=update.message.chat_id, latitude=closest_sensor_pos[0], longitude=closest_sensor_pos[1])
    response = """
Nächster Sensor: {closest_sensor}
Entfernung: {distance}
Messung: {value} Partikel pro m3

Schicke mir /setsensorid {closest_sensor}, um ihn als deinen Hauptsensor festzulegen
    """.format(closest_sensor=str(closest_sensor), distance=distance, value=str(modules.get_value(closest_sensor)))
    bot.send_message(chat_id=update.message.chat_id,
                     text=response)

    return ConversationHandler.END


@catch_error
def help(bot, update):
    help_message = """
Ich schicke dir eine Nachricht, wenn der Feinstaubgehalt deines Sensors über ein bestimmtes Limit steigt.

Du hast folgende Möglichkeiten:

/start - Einrichtung starten
/setsensorid - Sensor-ID festlegen
/setlimit - Limit festlegen

/getvalue - aktueller Wert deines Sensors
/details - Details über deinen Sensor
    """
    bot.send_message(chat_id=update.message.chat_id, text=help_message)

    return ConversationHandler.END


@catch_error
def not_command(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Leider kenne ich diesen Befehl mit. Verwende /help um alle Befehle zu sehen.")
    return ConversationHandler.END


@catch_error
def cancel(bot, update):
    logger.info("User {user} canceled the conversation.".format(user=update.message.from_user.username))
    bot.send_message(chat_id=update.message.chat_id,
                     text="Abgebrochen ...")
    return ConversationHandler.END


def error_callback(bot, update, error):
    try:
        raise error
    except Exception as e:
        logger.error(str(e))
        client.captureException()


def main():
    logger.info("Started bot.py")

    updater = Updater(token=config.bottoken)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("getvalue", getvalue),
            CommandHandler("setsensorid", setsensorid),
            CommandHandler("setlimit", setlimit),
            CommandHandler("details", details),
            CommandHandler("help", help),
            MessageHandler(Filters.location, location),
        ],

        states={
            START_SENSORID: [MessageHandler(Filters.text, start_setsensorid),
                             MessageHandler(Filters.location, start_setsensorid_location)],
            START_LIMIT: [MessageHandler(Filters.text, start_setlimit),]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error_callback)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    # Wait 10 seconds until network is available
    sleep(10)
    print("Started bot")
    main()
