import config
import sqlite3
import logging
from telegram.ext import Updater

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename="logs/news.log")
logger = logging.getLogger(__name__)

updater = Updater(token=config.bottoken)


def main():
    # Message input
    print("Your message (finish with '___'):")
    new_input = ""
    message = []
    while new_input != "___":
        new_input = input()
        message.append(new_input)

    # Delete ___ from list
    del message[-1]
    message = "\n".join(message)

    # Confirmation
    confirmation = input("Dou you really want to send? (yes/no): ")
    if confirmation.lower() != "yes":
        print("Canceled!")
        quit()

    # Connect to database
    conn = sqlite3.connect(config.database_location)
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    fetched_users = c.fetchall()
    c.close()
    conn.close()

    # Send message to every user
    for user in fetched_users:
        updater.bot.send_message(chat_id=user[2], text=message)

    logger.info("Send news to all users: {message}".format(message=message))

if __name__ == "__main__":
    main()
