#!/usr/bin/python3
# luftdaten-telegram.py

import modules
import config
import add_user

if __name__ == "__main__":
    modules.logging("Started luftdaten-telegram.py")

    users = modules.get_users_not_sent()
    for user in users:
        sensor_id = user[1]
        chat_id = user[2]
        limitation = user[3]

        # Get value
        value = int(modules.get_value(str(sensor_id)))

        # Send value if necessary
        if int(value) > int(limitation):
            modules.send("Achtung: Dein Feinstaubsensor hat " + str(value) + " Partikel pro m3 gemessen.", chat_id)
            modules.logging("Sent message to " + str(chat_id))
            modules.add_message_to_sent_message(chat_id)

    # Check for new users
    add_user.check_for_new_users()

    modules.logging("Finished luftdaten-telegram.py")
