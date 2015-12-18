#!/usr/bin/env python

from telegram import Updater
from telegram.dispatcher import run_async
from time import sleep
import logging
import sys

sys.path.insert(0, 'modules/image')
sys.path.insert(0, 'modules/qr_code')
sys.path.insert(0, 'modules/doge')
sys.path.insert(0, 'modules/fortune')
sys.path.insert(0, 'modules/speak')
import image
import qr_code
import doge
import fortune
import speak

root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = \
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

last_chat_id = 0

logger = logging.getLogger(__name__)

def help_command(bot, update):
    help_message = 'Help:\n\n' + image.help_command() + '\n'+ doge.help_command() + '\n'+ fortune.help_command() +\
                   '\n'+ qr_code.help_command() + '\n'+ speak.help_command()

    bot.sendMessage(chat_id=update.message.chat_id, text=help_message)

def test_command(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Hello")

def error(bot, update, error):
    """ Print error to console """
    logger.warn('Update %s caused error %s' % (update, error))

def main():
    # Create the EventHandler and pass it your bot's token.
    token = open('telegram_token.txt', 'r').read().strip()
    updater = Updater(token, workers=2)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.addTelegramCommandHandler("test", test_command)
    dp.addTelegramCommandHandler("image", image.image_command)
    dp.addTelegramCommandHandler("doge", doge.doge_command)
    dp.addTelegramCommandHandler("fortune", fortune.fortune_command)
    dp.addTelegramCommandHandler("qrcode", qr_code.qrcode_command)
    dp.addTelegramCommandHandler("speak", speak.speak_command)
    dp.addTelegramCommandHandler("help", help_command)

    dp.addErrorHandler(error)

    # Start the Bot and store the update Queue, so we can insert updates
    update_queue = updater.start_polling(poll_interval=0.1, timeout=20)

if __name__ == '__main__':
    main()
