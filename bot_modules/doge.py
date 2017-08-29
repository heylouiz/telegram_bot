#!/usr/bin/env python

import os
import requests
import subprocess

import telegram

command_name = "doge"

need_parameters = True

ask_for_parameters_text = "Me mande many frases separadas por virgulas." \
                          " Ex: such wow, very doge"

def help():
    return '/doge    - Manda um meme do doge com frases customizadas.\n' \
           ' - Usage: /doge frase1, frase2, frase3...\n'

@telegram.ext.dispatcher.run_async
def process_command(bot, update, args, user_data):
    if "-help" in args:
        update.message.reply_text(help())
        return

    # Inform that the bot will send an image
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)

    # Transform string "bla, ble, bli" in dogr.io/bla/ble/bli.png...
    wow_strings = " ".join(args)
    doge_url = "http://dogr.io/"
    doge_url += "/".join(wow_strings.split(","))
    doge_url += ".png?split=false"

    try:
        r = requests.get(doge_url)

        if r.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException as e:
        print(e)
        update.message.reply_text("Wow, very falha, so sorry, much erro.")

    unique_doge = "doge_" + str(update.message.message_id) + ".png"

    with open(unique_doge, "wb") as f:
        f.write(r.content)

    update.message.reply_photo(photo=open(unique_doge, "rb"))

    os.remove(unique_doge)
