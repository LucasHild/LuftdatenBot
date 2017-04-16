#!/usr/bin/python3
# add_user.py

import modules
import config
import requests
import re
import sqlite3

bottoken = config.bottoken


def check_for_new_users():
    """Retrieve new messages and checks for new users"""
    url = "https://api.telegram.org/bot" + bottoken + "/getUpdates"
    r = requests.get(url)
    result = r.json()["result"]
    messages = []
    for i in result:
        message = [i["message"]["text"], i["message"]["chat"]["id"]]
        messages.append(message)
    if len(messages) != 0:
        find_values(messages)


def find_values(messages):
    """Find sensor_id and limitation in messages"""
    for message in messages:
        chat_id = str(message[1])
        s = re.findall("sensor_id: \d+ limitation: \d+", message[0])
        if len(s) != 0:
            values = (re.findall("\d+", "".join(s)))
            sensor_id = values[0]
            limitation = values[1]
            add_user(sensor_id, chat_id, limitation)


def add_user(sensor_id, chat_id, limitation):
    """Check user and add to users"""
    # Check whether sensor_id is valid
    if modules.get_value(sensor_id) != False:
        modules.get_value(sensor_id)

        # Check whether chat_id is already in database
        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE chat_id = ?", (int(chat_id),))
        fetched_users = c.fetchall()
        c.close()
        conn.close()
        if fetched_users == []:  # not in database
            modules.add_user_to_db(sensor_id, chat_id, limitation)
            welcome(sensor_id, chat_id, limitation)
        else:  # already in database
            modules.logging("User " + chat_id + " registered twice")
    else:
        modules.logging("User " + chat_id + " registered with wrong sensor_id " + sensor_id)
        modules.send("Sensor " + sensor_id + " ist nicht verfügbar! Überprüfe deine Sensor ID.", chat_id)


def welcome(sensor_id, chat_id, limitation):
    """Send welcome message"""
    modules.send("Herzlich Willkommen bei [Luftdaten-Notification](https://github.com/Lanseuo/Luftdaten-Notification)!",
                 chat_id)
    modules.send("Deine Daten: Sensor-ID: " + sensor_id + " Limit: " + limitation + " Partikel pro m3", chat_id)
    value = modules.get_value(sensor_id)
    modules.send("Aktuell misst dein Feinstaub-Senosr: " + str(value) + " Partikel pro m3.", chat_id)
    modules.send("[Weitere Infos](https://github.com/Lanseuo/Luftdaten-Notification)", chat_id)
    modules.logging("Welcome message to " + chat_id)


if __name__ == "__main__":
    check_for_new_users()
