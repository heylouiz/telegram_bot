#!/usr/bin/env python
import json
import os
import requests
import random

import telegram

# Load config file from module directory
with open(os.path.join(os.path.dirname(__file__), 'config.json')) as config_file:
    CONFIGURATION = json.load(config_file)

command_name = "image"

need_parameters = True

ask_for_parameters_text = "What do you want to search?"

def help():
    return '/image - Get a random image.\n - Usage: /image word\n' +\
           'To teorically get the best image, use the options -best.\n - Usage: /image word -best\n'

def custom_search(query):
    r = requests.get("{}/image/{}".format(CONFIGURATION["services_server"], query))
    if r.status_code == 200:
        return r.json()
    return []

@telegram.ext.dispatcher.run_async
def process_command(bot, update, args, user_data):
    message = update.message.text

    if "-help" in args:
        update.message.reply_text(help())
        return

    # Inform that the bot will send an image
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)

    best = False
    if "-best" in args:
        best = True
        # Remove -best from arg list
        args.pop(args.index("-best"))

    search_string = " ".join(args)

    results = custom_search(search_string)

    if not results:
        update.message.reply_text("Could not find any images for {}", search_string)

    best_count = 0
    while True:
        best_count += 1
        try:
            photo = results[best_count] if best else random.choice(results)
            update.message.reply_photo(photo=photo)
            return
        except telegram.TelegramError as e:
            print(e)
            if best_count >= len(results):
                update.message.reply_text("Failed to send images for {}", search_string)
                return
            continue
