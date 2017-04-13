#!/usr/bin/python3
# luftdaten-telegram.py

import modules
import config
import add_user
import time


def already_sent_message(chat_id):
    """Check whether a message was already sent to chat_id today"""
    filename = "sent-users/sent-users-" + str(time.localtime()[0]) + "-" + str(time.localtime()[1]) + "-" + (str(time.localtime()[2])) + ".txt"
    try:
        with open(filename, "r") as f:
            file_content = f.read()
            f.close()
        chat_ids = file_content.split("\n")
        if chat_id in chat_ids:
            return True
        else:
            return False
    except: # if file doesn't already exist
        return False

def add_message_to_sent_message(chat_id):
    """Add message to sent-users"""
    filename = "sent-users/sent-users-" + str(time.localtime()[0]) + "-" + str(time.localtime()[1]) + "-" + (str(time.localtime()[2])) + ".txt"
    with open(filename, "a") as f:
        f.write(chat_id + "\n")
        f.close()

if __name__ == "__main__":
    modules.logging("Started luftdaten-telegram.py")

    users = modules.get_users()
    for user in users:
        sensor_id = user["sensor_id"]
        chat_id = user["chat_id"]
        limit = user["limit"]

        # Get value
        value = int(modules.get_value(sensor_id))

        # Send value if necessary
        if int(value) > int(limit):
            # Check whether a message to chat_id was already sent today
            if not already_sent_message(chat_id):
                modules.send("Dein Feinstaubsensor hat " + str(value) + " Partikel pro m3 gemessen.", chat_id)
                modules.logging("Sent message to " + chat_id)
                add_message_to_sent_message(chat_id)
            else:
                modules.logging("Not send message to " + chat_id + " (already sent one today)")

    # Check for new users
    add_user.check_for_new_users()

    modules.logging("Finished luftdaten-telegram.py")

