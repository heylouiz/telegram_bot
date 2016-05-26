#!/usr/bin/env python

import requests
import os
from telegram import ChatAction, ForceReply
from telegram.ext.dispatcher import run_async

from context import bot_context

def help_command():
    return '/doge    - Get a doge image meme with custom phrases.\n' \
           ' - Usage: /doge phrase1, phrase2, phrase3...\n'

@run_async
def doge_command(bot, update, args):
    message = update.message.text

    if "-help" in args:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.send_message(chat_id=update.message.chat_id, text=help_command())
        return

    if len(args) == 0:
        # Add this command as last command from user ID
        bot_context[update.message.from_user.id] = "doge"
        bot.send_message(chat_id=update.message.chat_id,
                        text='Send me the wow pharases separated by commas.'
                             ' Ex: such wow, very doge',
                        reply_to_message_id=update.message.message_id,
                        reply_markup=ForceReply(selective=True))
        return

    if message.find("/doge") >= 0: # If the command was directly called
        # Remove "/doge" from the message
        message = message.split(' ', 1)[1].strip()

    # Inform that the bot will send an image
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

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
        bot.send_message(chat_id=update.message.chat_id,
                        text="Wow, very failure, so sorry, much server error.",
                        reply_to_message_id=update.message.message_id)

    unique_doge = "doge_" + str(update.message.message_id) + ".png"

    with open(unique_doge, "wb") as f:
        f.write(r.content)

    bot.send_photo(chat_id=update.message.chat_id, photo=open(unique_doge, "rb"))

    os.remove(unique_doge)
