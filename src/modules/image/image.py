#!/usr/bin/env python

import requests
import sys
import random

from telegram import ChatAction
from telegram.ext.dispatcher import run_async

from telebot import CONFIGURATION

# Store preview request from chat
last_request = {} #pylint: disable=invalid-name

def help_command():
    return '/image - Get a random image.\n - Usage: /image word\n' +\
           'To teorically get the best image, use the options -best.\n - Usage: /image word -best\n'

# Send error message
def sendErrorMessage(bot, update, error_text):
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=error_text,
                    reply_to_message_id=update.message.message_id)


# Auxiliar function to sendPhoto
def sendImageMessage(bot, update, image_url):
    try:
        bot.sendPhoto(chat_id=update.message.chat_id, photo=image_url)
        return 0
    except Exception as e:
        print("/image error: " + str(e) + "\nLink: " + str(image_url))
        return -1

def lucasSearch(search_string):
    image_results = []

    try:
        url = "{}:2666/{}".format(CONFIGURATION["services_server"], search_string)
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

def googleSearch(search_string):
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


def bingSearch(search_string):
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
        sendErrorMessage(bot, update, "Wrong syntax. See /image -help.")
        return

    # Check parameters
    if "-help" in args:
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=help_command(),
                        reply_to_message_id=update.message.message_id)
        return

    if "-best" in args:
        message = message.replace("-best", "").strip()
        best = True

    # Remove "/image" from the message
    message = message.split(" ", 1)

    if more == False:
        if len(message) == 1:
            sendErrorMessage(bot, update, "Missing search string. See /image -help.")
            return
        else:
            message = message[1].strip()

    # Inform that the bot will send an image
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

    if update.message.chat_id in CONFIGURATION["image"]["special_groups"]:
        search_engine = "google"

    # Query string
    if more:
        try:
            search_string = last_request[update.message.chat_id]
        except KeyError:
            sendErrorMessage(bot, update, "No previous image search in this chat.")
            return
    else:
        search_string = message.strip()

    if search_engine == "google":
        (error_code, result) = googleSearch(search_string)
    elif search_engine == "lucas":
        (error_code, result) = lucasSearch(search_string)
    else:
        (error_code, result) = bingSearch(search_string)

    if error_code == 0:
        image_results = result
    else:
        sendErrorMessage(bot, update, result)
        return

    # If no image was found
    if len(image_results) == 0:
        sendErrorMessage(bot, update, "Could not find any images for {}".format(search_string.replace("%20", " ")))
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
        while sendImageMessage(bot, update, image_to_send) != 0:
            if timeout <= 0:
                sendErrorMessage(bot, update, "Failed to get image, try again.")
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
