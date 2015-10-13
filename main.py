#!/usr/bin/env python

import logging
import telebot
import urllib2

def main():
    global USER_IP

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create telegram bot
    bot = telebot.Telebot(open('telegram_token.txt', 'r').read().strip())

    # Get user ip
    try:
        ip = urllib2.urlopen('http://ip.42.pl/short').read()
    except:
        ip = '192.168.1.13'
        
    # Set ip used by bot
    bot.setIp(ip)

    # Run forever
    while True:
        bot.handleMessages()

if __name__ == '__main__':
    main()
