#!/usr/bin/env python

from telegram import ChatAction, ForceReply
from telegram.ext.dispatcher import run_async
import random

from context import bot_context

def help_command():
    return '/choose  - Randomly picks one of the given choices.\n - Usage: /choose yes, no\n'

@run_async
def choose_command(bot, update, args):
    message = update.message.text

    if "-help" in args:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.send_message(chat_id=update.message.chat_id, text=help_command())
        return

    if len(args) == 0:
        # Add this command as last command from user ID
        bot_context[update.message.from_user.id] = "choose"
        bot.send_message(chat_id=update.message.chat_id,
                        text="Send me the choices separated by commas (,). Ex: yes, no",
                        reply_to_message_id=update.message.message_id,
                        reply_markup=ForceReply(selective=True))
        return

    if message.find("/choose") >= 0: # If the command was directly called
        # Remove "/choose" from the message and create an array with the choices
        choices = message.split(' ', 1)[1].strip().split(",")
    else: # The command was triggered by a force reply
        choices = message.strip().split(",")

    if len(choices) <= 1:
        bot.send_message(chat_id=update.message.chat_id,
                        text="Wrong syntax. See /choose -help.",
                        reply_to_message_id=update.message.message_id)
        return

    # Inform that the bot will send a text 
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    bot.send_message(chat_id=update.message.chat_id,
                    text=random.choice(choices),
                    reply_to_message_id=update.message.message_id)

