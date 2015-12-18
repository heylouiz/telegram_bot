import os
import qrcode
import calendar
import time
from telegram import ChatAction
from telegram.dispatcher import run_async

def help_command():
    return '/qrcode  - Get a qrcode from given text.\n - Usage: /qrcode text to qrcode\n'

@run_async
def qrcode_command(bot, update):
    message = update.message.text
    message = message.split(' ', 1)[1].strip()

    if message.find("-help") >= 0:
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id, text=help_command())
        return

    # Inform that the bot will send an image
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

    img = qrcode.make(message)
    qrcode_unique = 'qrcode' + str(calendar.timegm(time.gmtime())) + '.jpg'

    img.save(qrcode_unique)

    bot.sendPhoto(chat_id=update.message.chat_id, photo=open(qrcode_unique, 'rb'))

    os.remove(qrcode_unique)
