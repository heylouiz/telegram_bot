#!/usr/bin/env python

import os
import requests
from urllib.parse import quote
from telegram import ChatAction, ForceReply
from telegram.ext.dispatcher import run_async

from telebot import CONFIGURATION

from context import bot_context

BASE_URL = "{}/speak/".format(CONFIGURATION["services_server"])

def help_command():
    return '/speak - Make the bot speak.\n- Usage: /speak text\n' +\
           'By default the bot speaks portuguese, use the parameter "-en" ' +\
           'to make it speak in english.\n- Usage: /speak -en text.\n' +\
           'You can change the gender of the bot using "-w", this will produce a female voice. ' +\
           'This works both in english (-en) and portuguese.\n-Usage: /speak -w text.\n'

@run_async
def speak_command(bot, update, args):
    message = update.message.text

    # Default is pt-br
    engine = "2"
    lang = "6" # Portuguese
    voice = "5" # Felipe

    if "-help" in args:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.send_message(chat_id=update.message.chat_id, text=help_command())
        return

    if len(args) == 0:
        # Add this command as last command from user ID
        bot_context[update.message.from_user.id] = "speak"
        bot.send_message(chat_id=update.message.chat_id,
                        text="Send me what do you want me to speak",
                        reply_to_message_id=update.message.message_id,
                        reply_markup=ForceReply(selective=True))
        return

    if "-en" in args:
        message = message.replace("-en", "").strip()
        engine = "4"
        voice = "5" # Daniel
        lang = "1" # English

    if "-pt" in args:
        message = message.replace("-pt", "").strip()

    if "-w" in args:
        message = message.replace("-w", "").strip()
        if "-en" in args:
            engine = "3"
            voice = "6" # Ashley
        else:
            voice = "4" # Fernanda


    if message.find("/speak") >= 0: # If the command was directly called
        message = message.split(" ", 1)[1] # Remove "/speak" from the message

    text_to_speak = message.strip()

    # Inform that the bot will send an audio file
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_AUDIO)

    # Make url
    encoded_text = quote(text_to_speak)
    url = BASE_URL + engine + "/" + lang + "/" + voice + "/" + encoded_text
    try:
        r = requests.get(url)

        if r.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException as e:
        print(e)
        bot.send_message(chat_id=update.message.chat_id,
                        text="Failed to create speak, server error.",
                        reply_to_message_id=update.message.message_id)
        return

    speak_unique = 'speak_' + str(update.message.message_id) + '.mp3'

    with open(speak_unique, 'wb') as speak_file:
        speak_file.write(r.content)

    try:
        bot.send_voice(chat_id=update.message.chat_id, voice=open(speak_unique, 'rb'))
    except Exception as e:
        bot.send_message(chat_id=update.message.chat_id, text='Failed to speak, try again')

    os.remove(speak_unique)
