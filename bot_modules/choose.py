#!/usr/bin/env python
import random
import telegram

command_name = "choose"

need_parameters = True

ask_for_parameters_text = "Send me the choices separated by commas (,). Ex: yes, no"

def help():
    return '/choose  - Randomly picks one of the given choices.\n - Usage: /choose yes, no\n'

@telegram.ext.dispatcher.run_async
def process_command(bot, update, args, user_data):
    if "-help" in args:
        update.message.reply_text(help())
        return

    choices = " ".join(args)

    if choices.find(",") < 0:
        update.message.reply_text("Wrong syntax.\n" + help())
        return

    # Inform that the bot will send a text
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    update.message.reply_text(random.choice(choices.split(",")))

