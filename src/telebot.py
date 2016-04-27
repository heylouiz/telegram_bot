#!/usr/bin/env python

from telegram import Updater
from telegram.dispatcher import run_async
from telegram.utils.botan import Botan
import json
import logging
import sys
import importlib
from enabled_modules import enabled_modules

# Load config file
with open('config.json') as config_file:
    CONFIGURATION = json.load(config_file)

# Create a Botan tracker object
botan = Botan(CONFIGURATION["botan_token"]) # pylint:disable=invalid-name

# Dinamically import enabled modules, edit file enabled_modules.py
bot_modules = {}
for module_name in CONFIGURATION["enabled_modules"]:
    sys.path.insert(0, 'modules/' + module_name)
    bot_modules[module_name] = importlib.import_module(module_name)

root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = \
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

logger = logging.getLogger(__name__)

def help_command(bot, update):
    help_message = "Help:\n\n"

    for module_name, module in bot_modules.items():
        help_message += getattr(module, "help_command")()

    bot.sendMessage(chat_id=update.message.chat_id, text=help_message)

def test_command(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Hello")

def any_message(bot, update):
    """ Print to console and log activity with Botan.io """
    botan.track(update.message,
                update.message.text.split(" ")[0])

    logger.info("New message\nFrom: %s\nchat_id: %d\nText: %s" %
                (update.message.from_user,
                 update.message.chat_id,
                 update.message.text))

def error(bot, update, error):
    """ Print error to console """
    logger.warn('Update %s caused error %s' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(CONFIGURATION["telegram_token"], workers=10)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Commands
    dp.addTelegramCommandHandler("test", test_command)
    dp.addTelegramCommandHandler("help", help_command)

    for module_name, module in bot_modules.items():
        # If the name of the module has a "_" in the name, the command should be his name without the "_".
        # Eg: module name: qr_code
        #     command: qrcode
        dp.addTelegramCommandHandler(module_name.replace("_", ""), getattr(module, module_name + "_command"))
        dp.addTelegramRegexHandler('^/' + module_name, any_message) # Handler to log requests

    dp.addTelegramCommandHandler("more", bot_modules["image"].image_command)

    # Other handlers
    dp.addErrorHandler(error)

    # Start the Bot and store the update Queue, so we can insert updates
    update_queue = updater.start_polling(poll_interval=0.1, timeout=20)

if __name__ == '__main__':
    main()
