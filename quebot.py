#!/usr/bin/env python

import logging
import telegram
import subprocess 
import urllib2
import simplejson
import random

LAST_UPDATE_ID = None
USER_IP = None
POOR_LOG = []

def main():
    global LAST_UPDATE_ID
    global USER_IP

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Telegram Bot Authorization Token
    bot = telegram.Bot('139638554:AAGzX3IfdAq9Bx1-tEpVv_jeZRge603PjPE')

    # Get user ip
    try:
        USER_IP = urllib2.urlopen('http://ip.42.pl/short').read()
    except:
        USER_IP = '192.168.1.13'

    # This will be our global variable to keep the latest update_id when requesting
    # for updates. It starts with the latest update_id if available.
    try:
        LAST_UPDATE_ID = bot.getUpdates()[-1].update_id
    except IndexError:
        LAST_UPDATE_ID = None

    while True:
        handle_message(bot)

def image_search_command(message):
    message = message.replace("/ibagem", "")
    message = message.strip()
    
    search_string = message.replace(" ", "%20")
    print search_string
    image_results = []

    for page in ['0', '4', '8']:
        url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
              'v=1.0&q=' + search_string + '&page=' + page + '&userip=' + USER_IP)
        print url
        request = urllib2.Request(url, None, {'Referer': 'www.quenerd.com.br'})
        response = urllib2.urlopen(request)

        results = simplejson.load(response)
        print results
        for r in range(len(results["responseData"]["results"])):
            image_results.append(results["responseData"]["results"][r]["url"])

    print image_results
    return random.choice(image_results)

def sed_command(message):
    message = message.replace("/sed", "")
    message = message.strip()

    (old, new) = message.split(" ")

    for msg in reversed(POOR_LOG):
        if msg.find(old) >= 0:
            return msg.replace(old, new)

def cowsay_command(message):
    message = message.replace("/cowsay", "")
    message = message.strip()

    cowsay_out = subprocess.Popen("cowsay " + message, stdout=subprocess.PIPE, shell=True)
    (output, err) = cowsay_out.communicate()
    
    return output

def fortune_command():
    fortune_out = subprocess.Popen("fortune", stdout=subprocess.PIPE, shell=True)
    (output, err) = fortune_out.communicate()
    
    return output

def calc_command(message):
    message = message.replace("/calc", "")
    message = message.strip()

    if message.find("@quebot"):
        message = message.replace("@quebot", "")


    if any(x in message for x in ['+', '-', '*', '^', '/']) == False:
        return "Invalid expression"

    try:
        return str(eval(message))
    except:
        return "Could not resolv the expression"

def handle_message(bot):
    global LAST_UPDATE_ID

    # Request updates after the last updated_id
    for update in bot.getUpdates(offset=LAST_UPDATE_ID, timeout=10):
        # chat_id is required to reply any message
        chat_id = update.message.chat_id
        message = update.message.text.encode('utf-8')    
        response = ''

        is_image = False
        ignore = False

        if (message):
            if message.find("/calc") >= 0:
                #response = calc_command(message)
                response = "Command not enabled, sry"
            elif message.find("/fortune") >= 0:
                response = fortune_command()
            elif message.find("/cowsay") >= 0:
                response = cowsay_command(message)
            elif message.find("/sed") >= 0:
                response = sed_command(message)
                response = "FTFY " + update.message.from_user.first_name + ":\n" + response
            elif message.find("/ibagem") >= 0:
                is_image = True
                response = image_search_command(message)
                print response
            elif message.find("/test") >= 0:
                response = 'Hello ' + update.message.from_user.first_name
            else:
                print message
                POOR_LOG.append(message)
                ignore = True

            if ignore == False:
                # Reply the message
                if is_image == False:
                    bot.sendMessage(chat_id=chat_id, text=response)
                else:
                    try:
                        bot.sendPhoto(chat_id=chat_id, photo=response)
                    except:
                        bot.sendMessage(chat_id=chat_id, text='Failed to get image, try again')
                    
            # Updates global offset to get the new updates
            LAST_UPDATE_ID = update.update_id + 1

if __name__ == '__main__':
    main()
