import sqlite3
from datetime import datetime

import config

conn = sqlite3.connect(config.database_location, check_same_thread=False)


def get_user(chat_id):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE chat_id = ?", [chat_id])
    user = c.fetchone()
    c.close()
    return user


def get_users_not_sent():
    """Get users from database where sent_today != today"""
    c = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM users WHERE sent_message != ?", (date,))
    data = c.fetchall()
    c.close()
    return data


def add_user_to_db(sensor_id, chat_id, limitation):
    """Save new user to users"""
    c = conn.cursor()

    c.execute(
        (
            "INSERT INTO users (sensor_id, chat_id, limitation, sent_message) "
            "VALUES (?, ?, ?, ?)"
        ),
        [sensor_id, chat_id, limitation, "never"]
    )

    conn.commit()
    c.close()


def add_message_to_sent_message(chat_id):
    c = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d")
    c.execute("UPDATE users SET sent_message = ? WHERE chat_id = ?",
              (date, int(chat_id)))

    conn.commit()
    c.close()


def set_sensor_id(chat_id, sensor_id):
    c = conn.cursor()
    c.execute(
        "UPDATE users SET sensor_id = (?) WHERE chat_id = (?)",
        [sensor_id, chat_id]
    )
    conn.commit()
    c.close()


def set_limitation(chat_id, limitation):
    c = conn.cursor()
    c.execute(
        "UPDATE users SET limitation = (?) WHERE chat_id = (?)",
        [limitation, chat_id]
    )
    conn.commit()
    c.close()
