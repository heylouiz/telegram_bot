#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import json
import logging
import os
import time

import telegram.ext

# Globals
found_modules = list()
loaded_modules = dict()
BOT_MODULES_DIR = "bot_modules"
logger = None
SEARCH_HISTORY_FILE = "search_history.json"
search_history = list()

# Search modules from directory
for f in os.listdir(BOT_MODULES_DIR):
    if f.find("__.py") >= 0:
        continue
    if f.find("module_example") >= 0:
        continue
    if f.endswith(".py") > 0:
        found_modules.append(f)

# Import modules found
for m in found_modules:
    name = m.split(".")[0]
    module = importlib.import_module(BOT_MODULES_DIR + "." + name)
    loaded_modules[name] = module

# Load search history json
with open(SEARCH_HISTORY_FILE) as f:
    search_history = json.load(f)

# Enable and configure logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Conversation handler states
ASK_FOR_TEXT = range(1)


def process_cmd(bot, update, args, user_data):
    """ Process the command """
    command_module = loaded_modules[user_data["command"]]
    command_module.process_command(bot, update, args, user_data)
    # If the command was image, store the search for future user
    if user_data["command"] == "image":
        with open(SEARCH_HISTORY_FILE, 'w') as f:
            global search_history
            search_history[str(update.message.chat_id)] = " ".join(args)
            json.dump(search_history, f)
    return done(bot, update, user_data)


def handle_cmd(bot, update, args, user_data):
    """ Handle a new command """
    # Log command
    log(update)
    text = update.message.text
    command = text.split()[0].replace("/", "").split("@")[0]
    user_data["command"] = command
    command_module = loaded_modules[command]
    # Check if theres something to query
    if command_module.need_parameters and "user_input" not in user_data and not args:
        # Stores the timestamp to timeout the conversation
        user_data["timestamp"] = int(time.time())
        update.message.reply_text(text=command_module.ask_for_parameters_text,
                                  reply_to_message_id=update.message.message_id,
                                  reply_markup=telegram.ForceReply(selective=True))
        return ASK_FOR_TEXT
    return process_cmd(bot, update, args, user_data)


def handle_user_input(bot, update, user_data):
    """ Handle user input to a previous command """
    # Checks if the conversation timedout
    if int(time.time()) - user_data["timestamp"] > 60:
        logger.info("Conversation timedout")
        return done(bot, update, user_data)
    text = update.message.text
    if text.find("/") == 0:
        command = text.split()[0].replace("/", "").split("@")[0]
        if command not in loaded_modules or command != user_data["command"]:
            update.message.reply_text("Busca invalida, tente novamente")
            return done(bot, update, user_data)
        if len(text.split(" ")) <= 1:
            user_data["command"] = command
            command_module = loaded_modules[command]
            # Check if theres something to query
            if command_module.need_parameters and "user_input" not in user_data:
                # Stores the timestamp to timeout the conversation
                user_data["timestamp"] = int(time.time())
                update.message.reply_text(text=command_module.ask_for_parameters_text,
                                          reply_to_message_id=update.message.message_id,
                                          reply_markup=telegram.ForceReply(selective=True))
                return ASK_FOR_TEXT
        else:
            text = text.split(" ", 1)[1]
    # Log user input
    log(update)
    user_data["user_input"] = text
    args = text.split()
    return process_cmd(bot, update, args, user_data)


def command_more(bot, update, user_data):
    chat_id_str = str(update.message.chat_id)
    if chat_id_str not in search_history:
        update.message.reply_text("Nenhuma busca antiga registrada, use o /image primeiro")
        return done(bot, update, {})
    user_data["command"] = "image"
    user_data["user_input"] = search_history[chat_id_str]
    args = user_data["user_input"].split()
    return process_cmd(bot, update, args, user_data)


def start(bot, update):
    """ Handle command start """
    update.message.reply_text(
            "Oi, eu sou o Quebot!\nDigite /help para ver a lista de comandos.\nCriador: @heylouiz")
    return telegram.ext.ConversationHandler.END


def help(bot, update):
    """ Handle command help """
    help_txt = ""
    for cmd, module in loaded_modules.items():
        help_txt += module.help()
    update.message.reply_text(help_txt)
    return telegram.ext.ConversationHandler.END


def done(bot, update, user_data):
    """ Finish conversation state machine """
    for key in user_data:
        del key
    user_data.clear()
    return telegram.ext.ConversationHandler.END


def error(bot, update, error):
    """ Log errors """
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def log(update):
    """ Generic log """
    logger.info("%s - %s" % (update.message.from_user.first_name, update.message.text))


def main():
    token = os.environ['TELEGRAM_TOKEN']
    # Create the Updater and pass it your bot's token.
    updater = telegram.ext.Updater(token, workers=20)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Generate command entry points from loaded modules
    command_entry_points = []
    for cmd, module in loaded_modules.items():
        command_entry_points.append(telegram.ext.CommandHandler(cmd, handle_cmd,
                                                                pass_args=True, pass_user_data=True))

    conv_handler = telegram.ext.ConversationHandler(
        entry_points=[telegram.ext.CommandHandler('start', start),
                      telegram.ext.CommandHandler('help', help),
                      telegram.ext.CommandHandler('more', command_more, pass_user_data=True)] + command_entry_points,
        states={
            ASK_FOR_TEXT: [telegram.ext.MessageHandler(telegram.ext.Filters.text,
                                                       handle_user_input,
                                                       pass_user_data=True),
                           telegram.ext.RegexHandler('^/.*',
                                                     handle_user_input,
                                                     pass_user_data=True)],
        },

        fallbacks=[telegram.ext.RegexHandler('^Done$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
