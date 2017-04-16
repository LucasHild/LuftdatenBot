#!/usr/bin/python3
# modules.py

import config
import requests
import time
import sqlite3

# Get bot information from config.py
bottoken = config.bottoken


def send(text, chat_id):
    """Send message via Telegram Bot"""
    url = "https://api.telegram.org/bot" + bottoken + "/getUpdates"
    r = requests.get(url)
    result = r.json()
    url = "https://api.telegram.org/bot" + bottoken + "/sendMessage"
    params = {"chat_id": str(chat_id), "text": text, "parse_mode": "Markdown"}
    r = requests.get(url, params=params)


def get_value(sensor_id):
    """Get value from Luftdaten-API"""
    try:
        data = requests.get("http://api.luftdaten.info/v1/sensor/" + sensor_id + "/",
                            headers={"Host": "api.luftdaten.info"}).json()[-1]["sensordatavalues"][0]["value"]
        data.encode("ascii")
        value = float(data)
        return value
    except:
        return False


def logging(text):
    """Log status to log/luftdaten-telegram + date + .log"""
    filename = "log/luftdaten-telegram-" + str(time.localtime()[0]) + "-" + str(time.localtime()[1]) + "-" +\
               (str(time.localtime()[2])) + ".log"
    logging_time = str(time.localtime()[3]) + ":" + str(time.localtime()[4]) + ":" + str(time.localtime()[5])
    with open(filename, "a") as f:
        f.write(logging_time + " - " + text + "\n")
        f.close()


def get_users():
    """Get users from database"""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def get_users_not_sent():
    """Get users from database where sent_today != today"""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    date = str(time.localtime()[0]) + "-" + str(time.localtime()[1]) + "-" + (str(time.localtime()[2]))
    c.execute("SELECT * FROM users WHERE sent_message != ?", (date,))
    data = c.fetchall()
    c.close()
    conn.close()
    return data


def add_user_to_db(sensor_id, chat_id, limitation):
    """Save new user to users"""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("INSERT INTO users (sensor_id, chat_id, limitation, sent_message) VALUES (?, ?, ?, ?)",
              (sensor_id, chat_id, limitation, "never"))

    conn.commit()
    c.close()
    conn.close()


def add_message_to_sent_message(chat_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    date = str(time.localtime()[0]) + "-" + str(time.localtime()[1]) + "-" + (str(time.localtime()[2]))
    c.execute("UPDATE users SET sent_message = ? WHERE chat_id = ?", (date, int(chat_id)))

    conn.commit()
    c.close()
    conn.close()

if __name__ == "__main__":
    logging("Test")