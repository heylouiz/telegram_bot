#!/usr/bin/env python

import telegram
import subprocess 
import urllib2
import simplejson
import random
from log_message import logMessage
import collections
import dota_handler

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
        
    def imageSearch(self, message):
        message = message.replace("/image", "")
        message = message.strip()
        
        search_string = message.replace(" ", "%20")
        image_results = []
    
        for page in ['0', '4', '8']:
            url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
                  'v=1.0&q=' + search_string + '&page=' + page + '&userip=' + self.ip + '&safe=active')
            request = urllib2.Request(url, None, {'Referer': 'www.quenerd.com.br'})
            response = urllib2.urlopen(request)
    
            results = simplejson.load(response)
            for r in range(len(results["responseData"]["results"])):
                image_results.append(results["responseData"]["results"][r]["url"])
    
	if len(image_results) == 0:
            self.sendTextMessage(message='Could not find any images for ' + search_string.replace("%20", " "))
        else:
            # Send image
            self.sendImageMessage(random.choice(image_results))
    
    def sed(self, message):
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
                self.sendTextMessage('Hey ' + logmsg.getUsername() + ' FTFT:\n' + reply_message)
    
    def fortune(self):
        fortune_out = subprocess.Popen("fortune", stdout=subprocess.PIPE, shell=True)
        output = fortune_out.communicate()[0]
        
        self.sendTextMessage(output)
    
    def dotaCommandHandler(self, message):
        message = message.replace("/dota", "")
        message = message.strip()
        
        # Handle the command and send the message to the user
        self.sendTextMessage(self.dota_handler.handleCommands(message))
        
    def sendTextMessage(self, message):
        try:
            self.bot.sendMessage(chat_id=self.chat_id, text=message.encode('utf-8'))
        except Exception as e:
            print "sendText Error: " + str(e)
            self.bot.sendMessage(chat_id=self.chat_id, text='There was an error, I don\'t know what happened :(')
            
    def sendImageMessage(self, image_url):
        try:
            self.bot.sendPhoto(chat_id=self.chat_id, photo=image_url.encode('utf-8'))
        except Exception as e:
            print "sendPhoto Error: " + str(e)
            self.sendTextMessage(message='Failed to get image, try again')
            
    def informTyping(self):
        self.bot.sendChatAction(chat_id=self.chat_id, action=telegram.ChatAction.TYPING)
        
    def informSendingPhoto(self):
        self.bot.sendChatAction(chat_id=self.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
        
    def handleMessages(self):
        # Request updates after the last updated_id
        for update in self.bot.getUpdates(offset=self.last_update_id, timeout=10):
            # chat_id is required to reply any message
            self.chat_id = update.message.chat_id
            message = update.message.text.encode('utf-8')    

            # Remove mention from message
            for mention in ["@quebot", "@Quebot"]:
                message = message.replace(mention, "")

            if (message):
                if message.find("/fortune") >= 0:
                    self.informTyping()
                    self.fortune()
                elif message.find("/replace") >= 0:
                    self.informTyping()
                    self.sed(message)
                elif message.find("/image") >= 0:
                    self.informSendingPhoto()
                    self.imageSearch(message)
                elif message.find("/dota") >= 0:
                    self.informTyping()
                    self.dotaCommandHandler(message)
                elif message.find("/test") >= 0:
                    self.informTyping()
                    self.sendTextMessage('Hello ' + update.message.from_user.first_name)
                else:
                    self.messagelog.append(logMessage(update.message.from_user.first_name, message))
    
                # Updates global offset to get the new updates
                self.last_update_id = update.update_id + 1
