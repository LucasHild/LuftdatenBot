import logging
import telegram
from telegram.ext import ConversationHandler

from bot import db, error, location_utils, luftdaten_service
from bot import START_SENSORID, START_LIMIT


logger = logging.getLogger(__name__)


@error.catch_error
def start(bot, update):
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    user = db.get_user(chat_id)

    if user:
        logger.info((f"User {username} called /start although "
                     "he is already in the database"))
        bot.send_message(
            chat_id=update.message.chat_id,
            text=("Du hast schon alles eingerichtet! Falls Du deine Daten "
                  "bearbeiten möchtest, wähle /setsensorid oder /setlimit.")
        )
        return ConversationHandler.END

    logger.info(f"Bot welcomes user {username}")
    bot.send_message(
        chat_id=update.message.chat_id,
        text=("Herzlich Willkommen zum "
              "[LuftdatenBot](https://github.com/Lanseuo/LuftdatenBot)!")
    )
    bot.send_message(
        chat_id=update.message.chat_id,
        text=("Wie lautet deine Sensor-ID? Schicke mir deine ID oder "
              "sende mir deinen Standort!"))
    return START_SENSORID


@error.catch_error
def start_setsensorid(bot, update):
    sensor_id = update.message.text
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    if not luftdaten_service.get_value(sensor_id):
        logger.info(
            f"User {username} registered with unavailable sensor_id {sensor_id}")
        bot.send_message(
            chat_id=update.message.chat_id,
            text=(f"Sensor {sensor_id} ist nicht verfügbar! Überprüfe deine "
                  "Sensor ID und führe gebe die ID erneut ein!"))
        return START_SENSORID

    db.add_user_to_db(sensor_id, chat_id, "")

    bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Deine Sensor-ID ({sensor_id}) wurde erfolgreich festgelegt!"
    )
    logger.info(f"User {username} set sensor_id  to {sensor_id}")

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Bei welchem Limit möchtest Du benachrichtigt werden?")
    return START_LIMIT


@error.catch_error
def start_setsensorid_location(bot, update):
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    latitude = update.message.location["latitude"]
    longitude = update.message.location["longitude"]

    logger.info(
        (f"User {username} sent location: {latitude} {longitude} "
         "at /start to setsensorid"))

    closest_sensor = location_utils.get_closest_sensor(latitude, longitude)

    bot.send_location(
        chat_id=chat_id,
        latitude=closest_sensor["latitude"],
        longitude=closest_sensor["longitude"]
    )

    value = luftdaten_service.get_value(closest_sensor["id"])

    response = f"""
Dieser Sensor wurde als dein Hauptsensor eingerichtet:

Nächster Sensor: {closest_sensor['id']}
Entfernung: {closest_sensor['distance']}
Messung: {value} Partikel pro m3"""

    bot.send_message(chat_id=chat_id, text=response)

    sensor_id = closest_sensor

    db.add_user_to_db(sensor_id, chat_id, "")

    logger.info(
        f"User {username} set sensor_id {sensor_id} with location at /start")

    bot.send_message(
        chat_id=update.message.chat_id,
        text="Bei welchem Limit möchtest Du benachrichtigt werden?"
    )
    return START_LIMIT


@error.catch_error
def start_setlimit(bot, update):
    limitation = update.message.text
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    db.set_limitation(chat_id, limitation)

    bot.send_message(
        chat_id=chat_id,
        text=(
            f"Dein Limit ({limitation}), bei dem Du benachrichtigt "
            "wirst, wurde erfolgreich geändert!"
        )
    )
    logger.info(f"User {username} set limit to {limitation} with /start")

    return ConversationHandler.END


@error.catch_error
def setsensorid(bot, update):
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    try:
        sensor_id = update.message.text.split(" ")[1]
    except IndexError:
        # Only command given (no value)
        logger.info("User {user} called /setsensorid without value")
        bot.send_message(
            chat_id=chat_id,
            text="Du musst einen Wert angeben! Beispiel: /setsensorid 000"
        )
        return ConversationHandler.END

    if not luftdaten_service.get_value(sensor_id):
        logger.info(
            f"User {username} registered with wrong sensor_id {sensor_id}")
        bot.send_message(
            chat_id=chat_id,
            text=(f"Sensor {sensor_id} ist nicht verfügbar! Überprüfe deine "
                  "Sensor ID und führe den Befehl erneut aus!"))
        return ConversationHandler.END

    user = db.get_user(chat_id)

    if not user:
        logger.info(
            (f"User {username} called /setsensorid "
                "not being in the database")
        )
        bot.send_message(
            chat_id=chat_id,
            text="Richte mich erst einmal mit /start ein!")
        return ConversationHandler.END

    db.set_sensor_id(chat_id, sensor_id)

    bot.send_message(
        chat_id=chat_id,
        text=f"Deine Sensor-ID ({sensor_id}) wurde erfolgreich verändert!")
    logger.info(
        f"User {username} updated sensor_id to {sensor_id} with /setsensorid")

    return ConversationHandler.END


@error.catch_error
def setlimit(bot, update):
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    try:
        limitation = update.message.text.split(" ")[1]
    except IndexError:
        # Only command given (no value)
        logger.info(
            f"User {username} called /setlimit without value")
        bot.send_message(
            chat_id=chat_id,
            text="Du musst einen Wert angeben! Beispiel: /setlimit 50")
        return ConversationHandler.END

    user = db.get_user(chat_id)

    if not user:
        logger.info(
            f"User {username} called /setlimit not being in the database")
        bot.send_message(chat_id=chat_id,
                         text="Richte mich erst einmal mit /start ein!")
        return ConversationHandler.END

    db.set_limitation(chat_id, limitation)

    bot.send_message(
        chat_id=chat_id,
        text=(f"Dein Limit ({limitation}), bei dem Du benachrichtigt wirst, "
              "wurde erfolgreich geändert!"))
    logger.info(f"User {username} set limit to {limitation} with /setlimit")

    return ConversationHandler.END


@error.catch_error
def getvalue(bot, update):
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    user = db.get_user(chat_id)

    if not user:
        logger.info(
            f"User {username} called /getvalue not being in the database")
        bot.send_message(chat_id=chat_id,
                         text="Du musst mich zuerst mit /start einrichten!")
        return ConversationHandler.END

    sensor_id = user[1]
    value = luftdaten_service.get_value(sensor_id)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Aktuell misst Dein Feinstaub-Sensor *{value} Partikel* pro m3.",
        parse_mode=telegram.ParseMode.MARKDOWN
    )
    logger.info(f"User {username} called /getvalue")

    return ConversationHandler.END


@error.catch_error
def details(bot, update):
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    user = db.get_user(chat_id)

    if not user:
        logger.info(
            f"User {username} called /setsensorid not being in the database")
        bot.send_message(
            chat_id=chat_id,
            text="Richte mich erst einmal mit /start ein!")
        return ConversationHandler.END

    value = luftdaten_service.get_value(user[1])

    bot.send_message(
        chat_id=update.message.chat_id,
        text=f"""
Sensor-ID: {user[1]}
Chat-ID: {chat_id}
Limit: {user[3]}
Messung: {value} Partikel pro m3""")
    return ConversationHandler.END


@error.catch_error
def location(bot, update):
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    latitude = update.message.location["latitude"]
    longitude = update.message.location["longitude"]

    logger.info(
        f"User {username} sent location: {latitude} {longitude}")

    closest_sensor = location_utils.get_closest_sensor(latitude, longitude)
    value = luftdaten_service.get_value(closest_sensor["sensor_id"])

    # Send response to user
    bot.send_location(
        chat_id=chat_id,
        latitude=closest_sensor["latitude"],
        longitude=closest_sensor["longitude"]
    )
    response = f"""
Nächster Sensor: {closest_sensor}
Entfernung: {closest_sensor["distance"]}
Messung: {value} Partikel pro m3

Schicke mir /setsensorid {closest_sensor["id"]}, um ihn als deinen Hauptsensor festzulegen
    """
    bot.send_message(
        chat_id=chat_id,
        text=response)

    return ConversationHandler.END


@error.catch_error
def help(bot, update):
    chat_id = update.message.chat_id
    answer = """
Ich schicke Dir eine Nachricht, wenn die Feinstaubbelastung deines Sensors über ein bestimmtes Limit steigt.

Du hast folgende Möglichkeiten:

/start - Einrichtung starten
/setsensorid - Sensor-ID festlegen
/setlimit - Limit festlegen

/getvalue - aktueller Wert deines Sensors
/details - Details über deinen Sensor"""
    bot.send_message(chat_id=chat_id, text=answer)

    return ConversationHandler.END


@error.catch_error
def unknown(bot, update):
    chat_id = update.message.chat_id

    bot.send_message(
        chat_id=chat_id,
        text=("Leider kenne ich diesen Befehl mit. "
              "Verwende /help um Dir alle Befehle anzeigen zu lassen."))
    return ConversationHandler.END


@error.catch_error
def cancel(bot, update):
    chat_id = update.message.chat_id
    username = update.message.from_user.username

    logger.info(f"User {username} canceled the conversation.")
    bot.send_message(
        chat_id=chat_id,
        text="Abgebrochen ...")
    return ConversationHandler.END
