#!/usr/bin/env python
import requests

from telegram.ext.dispatcher import run_async


def help():
    return '/doge    - Manda um meme do doge com frases customizadas.\n' \
           ' - Usage: /doge frase1, frase2, frase3...\n'


@run_async
def doge(update, context):
    if hasattr(update.message, 'text') and "-help" in update.message.text:
        update.message.reply_text(help())
        return

    # Transform string "bla, ble, bli" in dogr.io/bla/ble/bli.png...
    wow_strings = " ".join(context.args)
    doge_url = "http://dogr.io/"
    doge_url += "/".join(wow_strings.split(","))
    doge_url += ".png?split=false"

    try:
        r = requests.get(doge_url, stream=True)

        if r.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException:
        update.message.reply_text("Wow, very falha, so sorry, much erro.")

    update.message.reply_photo(photo=r.raw)
