# LuftdatenBot

![](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)
[![](https://img.shields.io/badge/Telegram-Bot-83bdfc.svg?style=flat-square)](http://t.me/LuftdatenBot)

A telegram bot ([@LuftdatenBot](http://t.me/LuftdatenBot)) which can be used with a respirable dust sensor by [Luftdaten.info](http://luftdaten.info/). You can access your data via telegram and you'll get a notification if the value exceeds a limit.

## Installation

### Download

```
git clone https://github.com/Lanseuo/LuftdatenBot.git
cd LuftdatenBot
pip3 install -r requirements.txt
```

### Create the bot

- open Telegram
- search for [@BotFather](http://t.me/BotFather)
- send /newbot and follow the instructions
- you will the token of your bot (keep it secret)

### Configuration

```
mv config-sample.py config.py
```

- open config.py and insert your token

## Usage

```
python3 bot.py
```

## Made with

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - telegram bot
- [Requests](https://github.com/requests/requests) - HTTP request library

## Meta

Lucas Hild - [https://lucas-hild.de](https://lucas.hild.de)  
This project is licensed under the MIT License - see the LICENSE file for details
