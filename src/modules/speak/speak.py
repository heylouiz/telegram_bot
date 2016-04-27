#!/usr/bin/env python

import os
import requests
from urllib.parse import quote
from telegram import ChatAction
from telegram.dispatcher import run_async

from telebot import CONFIGURATION

BASE_URL = "{}:2628/api/v1/tts/".format(CONFIGURATION["services_server"])

def help_command():
    return '/speak - Make the bot speak.\n- Usage: /speak text\n' +\
           'By default the bot speaks portuguese, use the parameter "-en" ' +\
           'to make it speak in english.\n- Usage: /speak -en text.\n' +\
           'You can change the gender of the bot using "-w", this will produce a female voice. ' +\
           'This works both in english (-en) and portuguese.\n-Usage: /speak -w text.\n'

@run_async
def speak_command(bot, update, **kwargs):
    message = update.message.text

    # Default is pt-br
    engine = "2"
    lang = "6" # Portuguese
    voice = "5" # Felipe

    if "-help" in kwargs["args"]:
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id, text=help_command())
        return

    if len(kwargs["args"]) == 0:
        bot.sendMessage(chat_id=update.message.chat_id, 
                        text="Wrong syntax. See /speak -help.",
                        reply_to_message_id=update.message.message_id)
        return

    if "-en" in kwargs["args"]:
        message = message.replace("-en", "").strip()
        engine = "4"
        voice = "5" # Daniel
        lang = "1" # English

    if "-pt" in kwargs["args"]:
        message = message.replace("-pt", "").strip()

    if "-w" in kwargs["args"]:
        message = message.replace("-w", "").strip()
        if "-en" in kwargs["args"]:
            engine = "3"
            voice = "6" # Ashley
        else:
            voice = "4" # Fernanda

    # Remove "/speak" from the message
    message = message.split(" ", 1)

    if len(message) == 1:
        bot.sendMessage(chat_id=update.message.chat_id, 
                        text="Missing text to speak. See /speak -help.",
                        reply_to_message_id=update.message.message_id)
        return
    else:
        text_to_speak = message[1].strip()

    # Inform that the bot will send an audio file
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_AUDIO)

    # Make url
    encoded_text = quote(text_to_speak)
    url = BASE_URL + encoded_text + "/" + engine + "/" + lang + "/" + voice + "/0/0/"
    try:
        r = requests.get(url)

        if r.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException as e:
        print(e)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Failed to create speak, server error.",
                        reply_to_message_id=update.message.message_id)
        return

    speak_unique = 'speak_' + str(update.message.message_id) + '.mp3'

    with open(speak_unique, 'wb') as speak_file:
        speak_file.write(r.content)

    try:
        bot.sendVoice(chat_id=update.message.chat_id, voice=open(speak_unique, 'rb'))
    except Exception as e:
        bot.sendMessage(chat_id=update.message.chat_id, text='Failed to speak, try again')

    os.remove(speak_unique)

