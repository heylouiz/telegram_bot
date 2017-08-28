#!/usr/bin/env python
import telegram

# The command name that the user should call on telegram "/helloworld"
command_name = "helloworld"

# If the command needs parameters, this one doesn't
need_parameters = False

# What the bot should reply to the user if he forget the parameters
ask_for_parameters_text = None

# The message replied by the bot when the user call "/helloworld -help"
def help():
    return '/module_example - Print Hello World!.\n - Usage: /module_example\n'

# The function that process the command
@telegram.ext.dispatcher.run_async # Decorator that makes the execution of this script assyncronous
def process_command(bot, update, args, user_data):

    # This needs to be here to reply to -help parameter
    if "-help" in args:
        update.message.reply_text(help())
        return

    # Inform that the bot will send a text message
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

    # Replies to user
    update.message.reply_text("Hello World!")
