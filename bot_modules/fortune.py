#!/usr/bin/env python
import os
import random
import subprocess

import telegram

command_name = "fortune"

need_parameters = False

ask_for_parameters_text = None

def help():
    return '/fortune - Manda um "pensamento".\n - Uso: /fortune [-pt pra mandar frases em português] \n'

@telegram.ext.dispatcher.run_async
def process_command(bot, update, args, user_data):
    if "-help" in args:
        update.message.reply_text(help())
        return

    database = "-a"
    if "-pt" in args:
        database = "/usr/share/games/fortunes/brasil"

    # Inform that the bot will send a text message
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    fortune_out = subprocess.Popen("fortune " + database, stdout=subprocess.PIPE, shell=True)
    output = fortune_out.communicate()[0]

    fortune_message = output.decode("utf-8")

    update.message.reply_text(fortune_message)
