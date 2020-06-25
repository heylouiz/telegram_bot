#!/usr/bin/env python
import os
import requests
import tempfile

from urllib.parse import quote
from telegram.ext.dispatcher import run_async

BASE_URL = "{}/speak".format(os.environ['API_SERVER'])


def help():
    return '/speak - Manda uma mensagem de voz com o texto.\n- Usage: /speak texto\n' +\
           'Para falar em inglês utilizar o parâmetro "-en". Uso: /speak -en text in english.' +\
           'Para usar uma voz feminina utilize o parâmetro "-w". Uso: /speak -w texto.\n'


@run_async
def speak(update, context):
    if hasattr(update.message, 'text') and "-help" in update.message.text:
        update.message.reply_text(help())
        return

    # Default is pt-br
    engine = "3"
    lang = "6"  # Portuguese
    voice = "2"  # Rafael

    args = context.args

    if "-en" in args:
        engine = "4"
        voice = "5"  # Daniel
        lang = "1"  # English
        args.pop(args.index("-en"))

    if "-pt" in args:
        args.pop(args.index("-pt"))

    if "-w" in args:
        if "-en" in args:
            engine = "3"
            voice = "6"  # Ashley
        else:
            engine = "3"
            voice = "1"  # Helena
        args.pop(args.index("-w"))

    text_to_speech = " ".join(args)

    if not text_to_speech:
        update.message.reply_text('Nada pra falar, coloque a frase a ser'
                                  ' falada na frente do comando "/speak cachorro quente"')
        return

    # Make speech url
    text_to_speech = quote(text_to_speech)
    url = f'{BASE_URL}/{engine}/{lang}/{voice}/{text_to_speech}'
    try:
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException:
        update.message.reply_text(text="Falha ao criar mensagem de voz.",
                                  reply_to_message_id=update.message.message_id)
        return

    try:
        update.message.reply_voice(voice=r.raw)
    except Exception:
        update.message.reply_text(text="Falha ao criar mensagem de voz.")
