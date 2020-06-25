#!/usr/bin/env python
import os
import random
import re
import requests

from contextlib import suppress

from telegram.ext.dispatcher import run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, TelegramError


def help():
    return '/image - Busca e manda uma imagem aleatória.\n - Uso: /image frase\n'


def custom_search(query):
    r = requests.get("{}/image/{}".format(os.environ['API_SERVER'], query))
    if r.status_code == 200:
        return r.json()
    return []


@run_async
def search_image(update, context, more=None):
    """Search a image for a given string"""
    if hasattr(update.message, 'text') and "-help" in update.message.text:
        update.message.reply_text(help())
        return

    if more:
        query = more['query']
    else:
        # Remove /image.* from message
        match = re.search(r'^/.*? (.*)', update.message.text)
        if match:
            query = match.group(1)
        else:
            update.message.reply_text('Nada pra buscar, coloque a palavra a ser'
                                      ' buscada na frente do comando "/image cachorro"')
            return

    results = custom_search(query)

    if not results:
        update.message.reply_text('Não encontrei nenhum resultado para a busca.')
        return

    keyboard = [[InlineKeyboardButton('Manda mais', callback_data=query)]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    for tries in range(0, 5):
        with suppress(TelegramError):
            if more:
                caption = 'Outra imagem de "%s" pedida por "%s"' % (more['query'], more['name'])
                context.bot.send_photo(photo=random.choice(results), chat_id=more['chat_id'],
                                       reply_markup=reply_markup, caption=caption)
            else:
                update.message.reply_photo(photo=random.choice(results), reply_markup=reply_markup)
            break


@run_async
def more_button(update, context):
    query = update.callback_query
    query.answer()
    search_image(update, context, {'query': query.data,
                                   'chat_id': query.message.chat_id,
                                   'name': query.from_user.name})
