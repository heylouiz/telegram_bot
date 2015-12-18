import requests
import sys
import random
sys.path.insert(0, 'modules/image')
import bing_key
from telegram import ChatAction
from telegram.dispatcher import run_async

def sendImageMessage(bot, update, image_url):
    print("SendImageMessage")
    try:
        bot.sendPhoto(chat_id=update.message.chat_id, photo=image_url)
        return 0
    except Exception as e:
        print("sendPhoto Error: " + str(e) + "\nLink: " + str(image_url))
        return -1

def help_command():
    return '/image   - Get a random image from search in Bing Images.\n - Usage: /image word\n' +\
           'To teorically get the best image, use the options -best.\n - Usage: /image word -best\n'

@run_async
def image_command(bot, update):
    message = update.message.text
    message = message.replace("/image", "").strip()

    if message.find("-help") >= 0:
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id, text=help_command())
        return

    # Inform that the bot will send an image
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_PHOTO)

    best = False

    if message.find("-best") >= 0:
        message = message.replace("-best", "")
        best = True

    search_string = message.strip()

    image_results = []

    url = 'https://api.datamarket.azure.com/Bing/Search/Image?' +\
          'Query=\'' + search_string + '\'&Adult=\'Moderate\'&Market=\'pt-BR\'&$format=json'
    r = requests.get(url, auth=(bing_key.keys[0], bing_key.keys[0]))
    results = r.json()
    for r in results["d"]["results"]:
        image_results.append(r["MediaUrl"])

    if len(image_results) == 0:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Could not find any images for ' + search_string.replace("%20", " "))
    else:
        # Use only the first 10 results
        image_results = image_results[0:10]

        # Send image
        if best:
            best_count = 0
            img_to_send = image_results[best_count]
        else:
            img_to_send = random.choice(image_results)

        timeout = 5
        while sendImageMessage(bot, update, img_to_send) != 0:
            if timeout <= 0:
                bot.sendMessage(chat_id=update.message.chat_id,
                                 text='Failed to get image, try again')
                break;
            if best:
                best_count += 1
                img_to_send = image_results[best_count]
            else:
                img_to_send = random.choice(image_results)
            if img_to_send == "":  # This should never happen
                img_to_send == image_results[0]
            timeout -= 1
