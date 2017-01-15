#!/usr/bin/env python

import requests
import sys
import random

from telegram import ChatAction, ForceReply
from telegram.ext.dispatcher import run_async

from telebot import CONFIGURATION

from context import bot_context

# Store preview request from chat
last_request = {} #pylint: disable=invalid-name

def help_command():
    return '/image - Get a random image.\n - Usage: /image word\n' +\
           'To teorically get the best image, use the options -best.\n - Usage: /image word -best\n'

# Send error message
def send_error_message(bot, update, error_text):
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id,
                    text=error_text,
                    reply_to_message_id=update.message.message_id)


# Auxiliar function to send_photo
def send_image_message(bot, update, image_url):
    try:
        bot.send_photo(chat_id=update.message.chat_id, photo=image_url)
        return 0
    except Exception as e:
        print("/image error: " + str(e) + "\nLink: " + str(image_url))
        return -1

def lucas_search(search_string):
    image_results = []

    try:
        url = "{}/image/{}".format(CONFIGURATION["services_server"], search_string)
        r = requests.get(url)

        # Check HTTP error code
        if r.status_code != 200:
            error_message = "Failed to get image. Server error, try again later."
            print(r.text)
            return (-1, error_message)

        results = r.json()

    except requests.exceptions.RequestException as e:
        print(e)
        error_message = "Failed to get image. Server error, try again later."
        return (-1, error_message)


    for r in results:
            image_results.append(r)

    return (0, image_results)

def google_search(search_string):
    image_results = []

    try:
        url = 'https://www.googleapis.com/customsearch/v1?'                +\
              'q=' + search_string                                         +\
              '&cx=' + CONFIGURATION["image"]["google_keys"][0]["cse_id"]  +\
              '&key=' + CONFIGURATION["image"]["google_keys"][0]["api_id"] +\
              '&searchType=image'                                          +\
              '&safe=medium'
        r = requests.get(url)

        # Check HTTP error code
        if r.status_code != 200:
            error_message = "Failed to get image. Server error, try again later."
            print(r.text)
            return (-1, error_message)

        results = r.json()

    except requests.exceptions.RequestException as e:
        print(e)
        error_message = "Failed to get image. Server error, try again later."
        return (-1, error_message)


    for r in results["items"]:
            image_results.append(r["link"])

    return (0, image_results)


def bing_search(search_string):
    image_results = []

    try:
        url = 'https://api.datamarket.azure.com/Bing/Search/Image?' +\
              'Query=\'' + search_string                            +\
              '\'&Adult=\'Moderate\''                               +\
              '&Market=\'pt-BR\''                                   +\
              '&$format=json'
        r = requests.get(url, auth=(CONFIGURATION["image"]["bing_keys"][0],
                                    CONFIGURATION["image"]["bing_keys"][0]))

        # Check HTTP error code
        if r.status_code != 200:
            error_message = "Failed to get image. Server error, try again later."
            print(r.text)
            return (-1, error_message)

        results = r.json()

    except requests.exceptions.RequestException as e:
        print(e)
        error_message = "Failed to get image. Server error, try again later."
        return (-1, error_message)


    for r in results["d"]["results"]:
        image_results.append(r["MediaUrl"])

    return (0, image_results)

@run_async
def image_command(bot, update, args):
    message = update.message.text

    # Command variables
    best = False
    more = False
    image_results = []
    search_string = ""
    search_engine = "lucas"
    timeout = 5
    global last_request

    if message.find("/more") >= 0:
        more = True

    if len(args) == 0 and more == False:
        # Add this command as last command from user ID
        bot_context[update.message.from_user.id] = "image"
        bot.send_message(chat_id=update.message.chat_id,
                        text="Send me what you wanna search. Ex: cute dogs",
                        reply_to_message_id=update.message.message_id,
                        reply_markup=ForceReply(selective=True))
        return

    # Check parameters
    if "-help" in args:
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.send_message(chat_id=update.message.chat_id,
                        text=help_command(),
                        reply_to_message_id=update.message.message_id)
        return

    if "-best" in args:
        message = message.replace("-best", "").strip()
        best = True

    if message.find("/image") >= 0 and not more: # If the command was directly called
        message = message.split(" ", 1)[1] # Remove "/image" from the message

    # Inform that the bot will send an image
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

    if update.message.chat_id in CONFIGURATION["image"]["special_groups"]:
        search_engine = "google"

    # Query string
    if more:
        try:
            search_string = last_request[update.message.chat_id]
        except KeyError:
            send_error_message(bot, update, "No previous image search in this chat.")
            return
    else:
        search_string = message.strip()

    if search_engine == "google":
        (error_code, result) = google_search(search_string)
    elif search_engine == "lucas":
        (error_code, result) = lucas_search(search_string)
    else:
        (error_code, result) = bing_search(search_string)

    if error_code == 0:
        image_results = result
    else:
        send_error_message(bot, update, result)
        return

    # If no image was found
    if len(image_results) == 0:
        send_error_message(bot, update, "Could not find any images for {}".format(search_string.replace("%20", " ")))
        return
    else:
        # Use only the first 10 results
        image_results = image_results[0:10]

        # If the parameter -best was used, the bot will try to return the most relevant search,
        # trying to send the first results, in order.
        if best:
            best_count = 0
            image_to_send = image_results[best_count]
        else:
            image_to_send = random.choice(image_results)

        # Tries to send image until timeout
        while send_image_message(bot, update, image_to_send) != 0:
            if timeout <= 0:
                send_error_message(bot, update, "Failed to get image, try again.")
                break;
            if best:
                best_count += 1
                image_to_send = image_results[best_count]
            else:
                image_to_send = random.choice(image_results)

            if image_to_send == "":  # This should never happen
                image_to_send == image_results[0]
            timeout -= 1

    # Save the  chat_id from last request
    last_request[update.message.chat_id] = search_string
