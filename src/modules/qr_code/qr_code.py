#!/usr/bin/env python

import os
import qrcode
from telegram import ChatAction
from telegram.ext.dispatcher import run_async

def help_command():
    return '/qrcode  - Get a qrcode from given text.\n - Usage: /qrcode text to qrcode\n'

@run_async
def qr_code_command(bot, update, args):
    message = update.message.text

    if "-help" in args:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.send_message(chat_id=update.message.chat_id, text=help_command())
        return

    if len(args) == 0:
        bot.send_message(chat_id=update.message.chat_id, 
                        text="Wrong syntax. See /qrcode -help.",
                        reply_to_message_id=update.message.message_id)
        return

    # Remove "/qrcode" from the message
    message = message.split(' ', 1)[1].strip()

    # Inform that the bot will send an image
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

    try:
        img = qrcode.make(message)

        qrcode_unique = "qrcode_" + str(update.message.message_id) + ".jpg"

        img.save(qrcode_unique)
    except:
        bot.send_message(chat_id=update.message.chat_id, 
                        text="Failed to create qrcode, try again.",
                        reply_to_message_id=update.message.message_id)
        return

    bot.send_photo(chat_id=update.message.chat_id, photo=open(qrcode_unique, 'rb'))

    os.remove(qrcode_unique)
