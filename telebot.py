#!/usr/bin/env python

import telegram
import subprocess
import requests
import json
import random
from log_message import logMessage
import collections
import dota.dota_handler as dota_handler
import shutil
import calendar
import time
import os

class Telebot:
    def __init__(self, auth_token):
        self.last_update_id = 0
        self.messagelog = collections.deque(maxlen=20)

        # Create Dota handler
        self.dota_handler = dota_handler.DotaHandler()

        # Create Telegram Bot using Authorization Token
        self.bot = telegram.Bot(auth_token)

        # Update the last update id
        try:
            self.last_update_id = self.bot.getUpdates()[-1].update_id
        except IndexError:
            self.last_update_id = None

    def setIp(self, ip):
        self.ip = ip

    # Handle the command /image
    # This command search a word (or more) in google images and reply with a image
    def imageSearch(self, message):
        message = message.replace("/image", "")
        message = message.strip()

        search_string = message.replace(" ", "%20")
        image_results = []

        for page in ['0', '4', '8']:
            url = ('https://ajax.googleapis.com/ajax/services/search/images?'
                  'v=1.0&q=' + search_string + '&page=' + page + '&userip=' + self.ip + '&safe=active')
            r = requests.get(url)
            results = r.json()
            for r in range(len(results["responseData"]["results"])):
                image_results.append(results["responseData"]["results"][r]["url"])

        if len(image_results) == 0:
            self.sendTextMessage(message='Could not find any images for ' + search_string.replace("%20", " "))
        else:
            # Send image
            img_to_send = random.choice(image_results)
            timeout = 5
            while self.sendImageMessage(img_to_send) != 0:
                if timeout <= 0:
                    self.sendTextMessage(message='Failed to get image, try again')
                    break;
                img_to_send = random.choice(image_results)
                if img_to_send == "":
                    img_to_send == image_results[0]
                timeout -= 1

    # Handle the command /replace
    # This commmand replace a word in a previous message.
    # Example: user John says: Hello frind
    # If a command "/replace frind/friend" is performed the bot will reply:
    # Hey John FTFY:\n Hello friend
    # The bot must be with privacy mode disabled to listen to all messages (Talk to @BotFather)
    #
    def replace(self, message):
        message = message.replace("/replace", "")
        message = message.strip()

        reply_message = ''

        message_splited = message.split("/")

        if len(message_splited) > 2:
            self.sendTextMessage("Could not perform the replace command\n Usage: /replace wrongword/correctword")
            return

        old = message_splited[0]
        new = message_splited[1]

        for logmsg in reversed(self.messagelog):
            if logmsg.getMessage().find(old) >= 0:

                # Send message
                reply_message = logmsg.getMessage().replace(old, new)
                self.sendTextMessage('Hey ' + logmsg.getUsername() + ' FTFY:\n' + reply_message)

    # Handle the command /doge
    # This command sends a doge meme with customized phrases
    # Reference to doge meme: knowyourmeme.com/memes/doge
    # You must have the imagemagick program in your linux system, the program
    # don't check if the command exist.
    # To install in debian derivates use this command: sudo apt-get install fortune
    def doge(self, message):
        message = message.replace("/doge", "")
        message = message.strip()

        wow_strings = message.split(",")

        doge_original = 'doge/doge.jpg'
        doge_unique = 'doge' + str(calendar.timegm(time.gmtime())) + '.jpg'

        # Copy the original doge file
        shutil.copy2(doge_original, doge_unique)

        # Read the color json
        with open('doge/doge_colors.json') as json_file:
            colors = json.load(json_file)

        # Uses imagemagick to put N strings in image
        for wow_str in wow_strings:
            convert_cmd = 'convert ' + doge_unique + ' -pointsize 40 -fill ' + str(random.choice(colors)) +\
                      ' -font Comic-Sans-MS-Bold -annotate +' + str(random.randint(0,600)) + '+' + str(random.randint(0,550)) +\
                      ' \'' + wow_str + '\' ' + doge_unique
            convert_out = subprocess.Popen(convert_cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]

        self.sendImage(open(doge_unique, 'rb'))

        os.remove(doge_unique)

    # Handle the command /fortune
    # This command simple execute the "fortune" command from linux shell.
    # You must have this program in order to use this bot command, the program
    # don't check if the command exist.
    # To install in debian derivates use this command: sudo apt-get install fortune
    def fortune(self):
        fortune_out = subprocess.Popen("fortune", stdout=subprocess.PIPE, shell=True)
        output = fortune_out.communicate()[0]
        self.sendTextMessage(output.decode("utf-8"))

    # Handle the command /dota
    def dotaCommandHandler(self, message):
        message = message.replace("/dota", "")
        message = message.strip()

        # Handle the command and send the message to the user
        self.sendTextMessage(self.dota_handler.handleCommands(message))

    # Handle the command /help
    def help(self):
        help_message = 'Available commands:\n' +\
        '/replace - Replace a word in a previous message.\n - Usage: /replace wrongword/correctword\n' +\
        '/fortune - Print a fortune message.\n - Usage: /fortune\n' +\
        '/image   - Get a image from Google Images.\n - Usage: /image word\n' +\
        '/doge    - Get a doge image meme with custom phrases.\n - Usage: /doge phrase1, phrase2, phrase3...\n' +\
        '/dota    - Get the last N matches played by a player in dota.\n - Usage: /dota nickname N\n'

        self.sendTextMessage(help_message)

    # Send text message
    def sendTextMessage(self, message):
        try:
            self.bot.sendMessage(chat_id=self.chat_id, text=message)
        except Exception as e:
            print("sendText Error: " + str(e))
            self.bot.sendMessage(chat_id=self.chat_id, text='There was an error, I don\'t know what happened :(')

    # Send image from url
    def sendImageMessage(self, image_url):
        try:
            self.bot.sendPhoto(chat_id=self.chat_id, photo=image_url)
            return 0 # No error
        except Exception as e:
            print("sendPhoto Error: " + str(e) + "\nLink: " + str(image_url))
            return -1

    # Send image from file
    def sendImage(self, image_file):
        try:
            self.bot.sendPhoto(chat_id=self.chat_id, photo=image_file)
        except Exception as e:
            print("sendPhoto Error: " + str(e))
            self.sendTextMessage(message='Failed to send image, try again')

    # Feedback to user informing that the bot will send a text message
    def informTyping(self):
        self.bot.sendChatAction(chat_id=self.chat_id, action=telegram.ChatAction.TYPING)

    # Feedback to user informing that the bot will send a photo
    def informSendingPhoto(self):
        self.bot.sendChatAction(chat_id=self.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)

    # Handle all messages received by the bot
    def handleMessages(self):
        # Request updates after the last updated_id
        for update in self.bot.getUpdates(offset=self.last_update_id, timeout=10):
            # chat_id is required to reply any message
            self.chat_id = update.message.chat_id
            message = update.message.text

            # Remove mention from message
            # When the bot is in a group chat it can be invoked with /command@botname so
            # we remove this from the message
            bot_username = self.bot.getMe()["username"]
            for mention in [bot_username, bot_username.title()]:
                message = message.replace('@' + mention, "")

            if (message):
                if message.startswith("/help"):
                    self.informTyping()
                    self.help()
                elif message.startswith("/fortune"):
                    self.informTyping()
                    self.fortune()
                elif message.startswith("/replace"):
                    self.informTyping()
                    self.replace(message)
                elif message.startswith("/image"):
                    self.informSendingPhoto()
                    self.imageSearch(message)
                elif message.startswith("/dota"):
                # This command doesn't work with all nicknames, need to be reworked
                #    self.sendTextMessage('Command disabled')
                    self.informTyping()
                    self.dotaCommandHandler(message)
                elif message.startswith("/doge"):
                    self.informSendingPhoto()
                    self.doge(message)
                elif message.startswith("/test"):
                    self.informTyping()
                    self.sendTextMessage('Hello ' + update.message.from_user.first_name)
                else:
                    self.messagelog.append(logMessage(update.message.from_user.first_name, message))

                # Updates global offset to get the new updates
                self.last_update_id = update.update_id + 1
