#!/usr/bin/python3
# add_user.py

import modules
import config
import requests
import re

bottoken = config.bottoken
config.users

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
    """Find sensor_id and limit in messages"""
    for message in messages:
        chat_id = str(message[1])
        s = re.findall("sensor_id: \d+ limit: \d+", message[0])
        if len(s) != 0:
            values = (re.findall("\d+", "".join(s)))
            sensor_id = values[0]
            limit = values[1]
            add_user(sensor_id, chat_id, limit)

def add_user(sensor_id, chat_id, limit):
    """Check user and add to users"""
    # Check whether sensor_id is valid
    if modules.get_value(sensor_id) != False:
        modules.get_value(sensor_id)
        # Check whether chat_id is already in users.txt
        users = modules.get_users()
        list_with_chat_ids = []
        for user in users:
            list_with_chat_ids.append(user["chat_id"])
        if chat_id not in list_with_chat_ids:

            modules.add_user(sensor_id, chat_id, limit)
            welcome(sensor_id, chat_id, limit)
        else:
            modules.logging("User " + chat_id + " registered twice")
    else:
        modules.logging("User " + chat_id + " registered with wrong sensor_id " + sensor_id)
        modules.send("Sensor " + sensor_id + " ist nicht verfügbar! Überprüfe deine Sensor ID.", chat_id)

def welcome(sensor_id, chat_id, limit):
    """Send welcome message"""
    modules.send("Herzlich Willkommen bei [Luftdaten-Notification](https://github.com/Lanseuo/Luftdaten-Notification)!", chat_id)
    modules.send("Deine Daten: Sensor-ID: " + sensor_id + " Limit: " + limit + " Partikel pro m3", chat_id)
    value = modules.get_value(sensor_id)
    modules.send("Aktuell misst dein Feinstaub-Senosr: " + str(value) + " Partikel pro m3.", chat_id)
    modules.send("[Weitere Infos](https://github.com/Lanseuo/Luftdaten-Notification)", chat_id)
    modules.logging("Welcome message to " + chat_id)

if __name__ == "__main__":
    check_for_new_users()