#!/usr/bin/env python
import random
from telegram.ext.dispatcher import run_async


def help():
    return '/choose  - Escolhe uma das opções disponíveis\n - Uso: /choose sim, não\n'


@run_async
def choose(update, context):
    if hasattr(update.message, 'text') and "-help" in update.message.text:
        update.message.reply_text(help())
        return

    choices = " ".join(context.args)

    if choices.find(",") < 0:
        update.message.reply_text("Parametros inválidos.\n" + help())
        return

    update.message.reply_text(random.choice(choices.split(",")))
