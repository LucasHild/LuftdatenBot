import bot.db as db
import bot.luftdaten_service as luftdaten_service


def check_for_exceeds(bot, job):
    return
    # Get logger and client from job context
    logger = job.context["logger"]
    client = job.context["client"]

    try:
        users = db.get_users_not_sent()
        for user in users:
            sensor_id = user[1]
            chat_id = int(user[2])
            limitation = user[3]

            value = luftdaten_service.get_value(str(sensor_id))
            if not value:
                return

            if value > limitation:
                bot.send_message(
                    chat_id=chat_id,
                    text=(f"Achtung: Dein Feinstaubsensor hat {value} "
                          "Partikel pro m3 gemessen.")
                )
                logger.info(f"Sent message to {chat_id}")
                db.add_message_to_sent_message(chat_id)

    except Exception as e:
        logger.error(str(e))
        client.captureException()
