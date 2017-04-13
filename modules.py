#!/usr/bin/python3
# modules.py

import config
import requests
import time

# Get bot information from config.py
bottoken = config.bottoken
webmaster_chat_id = config.webmaster_chat_id
users = config.users

def send(text, chat_id):
    """Send message via Telegram Bot"""
    url = "https://api.telegram.org/bot" + bottoken + "/getUpdates"
    r = requests.get(url)
    result = r.json()
    url = "https://api.telegram.org/bot" + bottoken + "/sendMessage"
    params = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    r = requests.get(url, params=params)


def get_value(sensor_id):
    """Get value from Luftdaten-API"""
    try:
        data = requests.get("http://api.luftdaten.info/v1/sensor/" + sensor_id + "/", headers={"Host": "api.luftdaten.info"}).json()[-1]["sensordatavalues"][0]["value"]
        data.encode("ascii")
        value = float(data)
        return value
    except:
        return False

def logging(text):
    """Log status to log/luftdaten-telegram + date + .log"""
    filename = "log/luftdaten-telegram-" + str(time.localtime()[0]) + "-" + str(time.localtime()[1]) + "-" + (str(time.localtime()[2])) + ".log"
    logging_time = str(time.localtime()[3]) + ":" + str(time.localtime()[4]) + ":" + str(time.localtime()[5])
    with open(filename, "a") as f:
        f.write(logging_time + " - " + text + "\n")
        f.close()

def get_users():
    """Get users from users.txt"""
    # users.txt is saved in this format: sensor_id-chat_id-limit
    with open("users.txt", "r") as f:
        file_content = f.read()
        f.close()
    list_with_users = file_content.split("\n")
    users = []
    for line in list_with_users:
        line = line.split("-")
        if len(line) == 3: # removes empty entries
            user_dictionary = {"sensor_id": line[0], "chat_id": line[1], "limit": line[2]}
            users.append(user_dictionary)
    return users

def add_user(sensor_id, chat_id, limit):
    """Save new user to users"""
    # Add user to list
    user_dictionary = {"sensor_id": sensor_id, "chat_id": chat_id, "limit": limit}
    users = get_users()
    users.append(user_dictionary)

    # Generate new file
    joined_values = []
    for user in users:
        line = user["sensor_id"] + "-" + user["chat_id"] + "-" + user["limit"]
        joined_values.append(line)
    file_content = "\n".join(joined_values)
    print(file_content)

    # Save file
    with open("users.txt", "w") as f:
        f.write(file_content)
        f.close()
    logging("Add user " + chat_id + " to list")