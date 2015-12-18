import shutil
import os
import subprocess
import calendar
import time
import json
import random
from telegram import ChatAction
from telegram.dispatcher import run_async

def help_command():
    return '/doge    - Get a doge image meme with custom phrases.\n - Usage: /doge phrase1, phrase2, phrase3...\n'

@run_async
def doge_command(bot, update):
    message = update.message.text
    message = message.replace("/doge", "").strip()

    if message.find("-help") >= 0:
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id, text=help_command())
        return

    # Inform that the bot will send an image
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

    wow_strings = message.split(",")

    current_dir = os.path.dirname(os.path.abspath(__file__)) + '/'
    doge_original = current_dir + 'doge.jpg'
    doge_unique = 'doge' + str(calendar.timegm(time.gmtime())) + '.jpg'

    # Copy the original doge file
    shutil.copy2(doge_original, doge_unique)

    # Read the color json
    with open(current_dir + 'doge_colors.json') as json_file:
        colors = json.load(json_file)

    # Uses imagemagick to put N strings in image
    for wow_str in wow_strings:
        convert_cmd = 'convert ' + doge_unique + ' -pointsize 40 -fill ' + str(random.choice(colors)) +\
                  ' -font Comic-Sans-MS-Bold -annotate +' + str(random.randint(0,600)) + '+' + str(random.randint(0,550)) +\
                  ' \'' + wow_str + '\' ' + doge_unique
        convert_out = subprocess.Popen(convert_cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]

    try:
        bot.sendPhoto(chat_id=update.message.chat_id, photo=open(doge_unique, 'rb'))
    except Exception as e:
        print("sendPhoto Error: " + str(e))
        bot.sendMessage(chat_id=update.message.chat_id, text='Failed to send image, try again')

    os.remove(doge_unique)
