from time import sleep

import bot

if __name__ == "__main__":
    # Wait 10 seconds until network is available
    sleep(10)
    print("Started bot")
    bot.main()
