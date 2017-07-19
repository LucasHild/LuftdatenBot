#!/usr/bin/python3
# modules.py

import config
import requests
import time
import sqlite3


def get_value(sensor_id):
    """Get value from Luftdaten-API"""
    sensor_id = str(sensor_id)
    try:
        data = requests.get("http://api.luftdaten.info/v1/sensor/" + str(sensor_id) + "/",
                            headers={"Host": "api.luftdaten.info"}).json()[-1]["sensordatavalues"][0]["value"]
        data.encode("ascii")
        value = float(data)
        return value
    except:
        return False


def get_users():
    """Get users from database"""
    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def get_users_not_sent():
    """Get users from database where sent_today != today"""
    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()

    date = str(time.localtime()[0]) + "-" + str(time.localtime()[1]) + "-" + (str(time.localtime()[2]))
    c.execute("SELECT * FROM users WHERE sent_message != ?", (date,))
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def add_user_to_db(sensor_id, chat_id, limitation):
    """Save new user to users"""
    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()

    c.execute("INSERT INTO users (sensor_id, chat_id, limitation, sent_message) VALUES (?, ?, ?, ?)",
              (sensor_id, chat_id, limitation, "never"))

    conn.commit()
    c.close()
    conn.close()


def add_message_to_sent_message(chat_id):
    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()

    date = str(time.localtime()[0]) + "-" + str(time.localtime()[1]) + "-" + (str(time.localtime()[2]))
    c.execute("UPDATE users SET sent_message = ? WHERE chat_id = ?", (date, int(chat_id)))

    conn.commit()
    c.close()
    conn.close()