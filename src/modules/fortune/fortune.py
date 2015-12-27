#!/usr/bin/env python

import subprocess
from telegram import ChatAction
from telegram.dispatcher import run_async

def help_command():
    return '/fortune - Print a fortune message.\n - Usage: /fortune\n'

@run_async
def fortune_command(bot, update, **kwargs):
    message = update.message.text
    message = message.replace("/fortune", "").strip()

    database = "-a"

    if "-help" in kwargs["args"]:
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id, text=help_command())
        return

    if "-pt" in kwargs["args"]:
        database = "/usr/share/games/fortunes/brasil"

    # Inform that the bot will send a text message
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    fortune_out = subprocess.Popen("fortune " + database, stdout=subprocess.PIPE, shell=True)
    output = fortune_out.communicate()[0]

    fortune_message = output.decode("utf-8")

    bot.sendMessage(chat_id=update.message.chat_id, text=fortune_message)
