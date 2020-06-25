#!/usr/bin/env python
import subprocess

from telegram.ext.dispatcher import run_async


def help():
    return '/fortune - Manda um "pensamento".\n - Uso: /fortune\n'


@run_async
def fortune(update, context):
    if hasattr(update.message, 'text') and "-help" in update.message.text:
        update.message.reply_text(help())
        return

    database = "-a"

    fortune_out = subprocess.Popen("fortune " + database, stdout=subprocess.PIPE, shell=True)
    update.message.reply_text(fortune_out.communicate()[0].decode("utf-8"))
