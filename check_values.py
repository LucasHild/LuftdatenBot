import modules

def check(bot, job):
    # Get logger and client from job context
    logger = job.context["logger"]
    client = job.context["client"]

    try:
        logger.info("Started check_values.check()")

        users = modules.get_users_not_sent()
        for user in users:
            sensor_id = user[1]
            chat_id = user[2]
            limitation = user[3]

            # Get value
            value = int(modules.get_value(str(sensor_id)))

            # Send value if necessary
            if int(value) > int(limitation):
                bot.send_message(chat_id=int(chat_id),
                                 text="Achtung: Dein Feinstaubsensor hat " + str(value) + " Partikel pro m3 gemessen.")
                logger.info("Sent message to " + str(chat_id))
                modules.add_message_to_sent_message(chat_id)

        logger.info("Finished check_values.check()")
    except Exception as e:
        logger.error(str(e))
        client.captureException()
