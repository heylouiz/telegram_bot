#!/usr/bin/env python
import subprocess

from telegram.ext.dispatcher import run_async


def help():
    return '/fortune - Manda um "pensamento".\n - Uso: /fortune [-pt pra mandar frases em português] \n'


@run_async
def fortune(bot, update, args):
    if hasattr(update.message, 'text') and "-help" in update.message.text:
        update.message.reply_text(help())
        return

    database = "-a"
    if "-pt" in args:
        database = "/usr/share/games/fortunes/brasil"

    fortune_out = subprocess.Popen("fortune " + database, stdout=subprocess.PIPE, shell=True)
    update.message.reply_text(fortune_out.communicate()[0].decode("utf-8"))
