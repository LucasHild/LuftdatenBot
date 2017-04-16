# Telegram Configuration
Telegram allows you to develop your own bot. But don't worry: You don't have to type any code. In this guide you will learn how to configure the notification bot.

## Your Information
### Sensor-ID
Every respirable dust sensor has it's own ID. It can be found on the [map](http://maps.luftdaten.info/).
![Sensor-ID on the map](https://lab.lucas-hild.de/github/Luftdaten-Notification/sensor-id.png)

### Limitation
Every time the value exceeds the limit you'll get a notification via Telegram. Think about a limit, when you'll be notified. A possible value would be for example 50 particles per m3.

## Message to bot
Next you'll have to start a conversation with [@LuftdatenBot](https://t.me/LuftdatenBot). Write a message with your information to the bot:

```
sensor_id: 000 limitation: 50
```

The message has to look exactly like this (apart from the values). Wait about 5 minutes and you'll get a respond by the bot. Now everything is configured.

![chat with bot](https://lab.lucas-hild.de/github/Luftdaten-Notification/bot.png)

If there are any bugs, please tell me: lucaslanseuo (at) gmail (dot) com!