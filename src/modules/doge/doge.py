#!/usr/bin/env python

import requests
import os
from telegram import ChatAction
from telegram.dispatcher import run_async

def help_command():
    return '/doge    - Get a doge image meme with custom phrases.\n - Usage: /doge phrase1, phrase2, phrase3...\n'

@run_async
def doge_command(bot, update, **kwargs):
    message = update.message.text

    if "-help" in kwargs["args"]:
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id, text=help_command())
        return

    if len(kwargs["args"]) == 0:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Wrong syntax. See /doge -help.",
                        reply_to_message_id=update.message.message_id)
        return

    # Remove "/doge" from the message
    message = message.split(' ', 1)[1].strip()

    # Inform that the bot will send an image
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

    wow_strings = message.split(",")

    doge_url = "http://dogr.io/"
    for wow in wow_strings:
        doge_url += wow.strip() + "/"
    doge_url = doge_url[:-1] # Remove last / from url
    doge_url += ".png?split=false"

    try:
        r = requests.get(doge_url)

        if r.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException as e:
        print(e)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Wow, very failure, so sorry, much server error.",
                        reply_to_message_id=update.message.message_id)

    unique_doge = "doge_" + str(update.message.message_id) + ".png"

    with open(unique_doge, "wb") as f:
        f.write(r.content)

    bot.sendPhoto(chat_id=update.message.chat_id, photo=open(unique_doge, "rb"))

    os.remove(unique_doge)
