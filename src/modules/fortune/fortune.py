#!/usr/bin/env python

import subprocess
from telegram import ChatAction
from telegram.ext.dispatcher import run_async

def help_command():
    return '/fortune - Print a fortune message.\n - Usage: /fortune\n'

@run_async
def fortune_command(bot, update, args):
    message = update.message.text
    message = message.replace("/fortune", "").strip()

    database = "-a"

    if "-help" in args:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.send_message(chat_id=update.message.chat_id, text=help_command())
        return

    if "-pt" in args:
        database = "/usr/share/games/fortunes/brasil"

    # Inform that the bot will send a text message
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    fortune_out = subprocess.Popen("fortune " + database, stdout=subprocess.PIPE, shell=True)
    output = fortune_out.communicate()[0]

    fortune_message = output.decode("utf-8")

    bot.send_message(chat_id=update.message.chat_id, text=fortune_message)
