#!/usr/bin/env python

from telegram import ChatAction
from telegram.ext.dispatcher import run_async
import random

def help_command():
    return '/choose  - Randomly picks one of the given choices.\n - Usage: /choose yes, no\n'

@run_async
def choose_command(bot, update, args):
    message = update.message.text

    if "-help" in args:
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id, text=help_command())
        return

    if len(args) == 0:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Wrong syntax. See /choose -help.",
                        reply_to_message_id=update.message.message_id)
        return

    # Remove "/choose" from the message
    choices = message.split(' ', 1)[1].strip().split(",")

    if len(choices) <= 1:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Wrong syntax. See /choose -help.",
                        reply_to_message_id=update.message.message_id)
        return

    # Inform that the bot will send a text 
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    bot.sendMessage(chat_id=update.message.chat_id,
                    text=random.choice(choices),
                    reply_to_message_id=update.message.message_id)

