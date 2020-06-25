#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)

from commands import image, speak, choose, fortune, doge


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Globals
logger = logging.getLogger(__name__)

START_MESSAGE = 'Oi, eu sou o Quebot!\nDigite /help para ver a lista de comandos.\nCriador: @heylouiz'

HELP_MESSAGE = ('/doge    - Manda um meme do doge com frases customizadas.\n'
                '- Usage: /doge frase1, frase2, frase3...\n'
                '/image - Busca e manda uma imagem aleatória.\n'
                '- Uso: /image frase\n'
                '/choose  - Escolhe uma das opções disponíveis\n'
                '- Uso: /choose sim, não\n'
                '/speak - Manda uma mensagem de voz com o texto.\n'
                '- Usage: /speak texto\n'
                'Para falar em inglês utilizar o parâmetro "-en". Uso: /speak -en text in english.'
                ' Para usar uma voz feminina utilize o parâmetro "-w". Uso: /speak -w texto.\n'
                '/fortune - Manda um "pensamento".\n'
                '- Uso: /fortune [-pt pra mandar frases em português]')


# Command functions
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(START_MESSAGE)


def help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text(HELP_MESSAGE)


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('image', image.search_image))
    dp.add_handler(CommandHandler('speak', speak.speak))
    dp.add_handler(CommandHandler('choose', choose.choose))
    dp.add_handler(CommandHandler('fortune', fortune.fortune))
    dp.add_handler(CommandHandler('doge', doge.doge))

    # Add inline button handlers
    dp.add_handler(CallbackQueryHandler(image.more_button))

    # Add error handler
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
