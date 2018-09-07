#!/usr/bin/env python
import os
import requests
from urllib.parse import quote
import telegram

BASE_URL = "{}/speak/".format(os.environ['API_SERVER'])

command_name = "speak"

need_parameters = True

ask_for_parameters_text = "O que você quer que eu diga?"


def help():
    return '/speak - Manda uma mensagem de voz com o texto.\n- Usage: /speak texto\n' +\
           'Para falar em inglês utilizar o parâmetro "-en". Uso: /speak -en text in english.' +\
           'Para usar uma voz feminina utilize o parâmetro "-w". Uso: /speak -w texto.\n'


@telegram.ext.dispatcher.run_async
def process_command(bot, update, args, user_data):
    if "-help" in args:
        update.message.reply_text(help())
        return

    # Default is pt-br
    engine = "3"
    lang = "6"  # Portuguese
    voice = "2"  # Rafael

    # Inform that the bot will send a voice message
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.UPLOAD_AUDIO)

    if "-en" in args:
        engine = "4"
        voice = "5"  # Daniel
        lang = "1"  # English
        args.pop(args.index("-en"))

    if "-pt" in args:
        args.pop(args.index("-pt"))

    if "-w" in args:
        if "-en" in args:
            engine = "3"
            voice = "6"  # Ashley
        else:
            voice = "1"  # Helena
        args.pop(args.index("-w"))

    text_to_speech = " ".join(args)

    # Make speech url
    encoded_text = quote(text_to_speech)
    url = BASE_URL + engine + "/" + lang + "/" + voice + "/" + encoded_text
    try:
        r = requests.get(url)
        if r.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException as e:
        print(e)
        update.message.reply_text(text="Falha ao criar mensagem de voz.",
                                  reply_to_message_id=update.message.message_id)
        return

    speak_unique = 'speak_' + str(update.message.message_id) + '.mp3'

    with open(speak_unique, 'wb') as speak_file:
        speak_file.write(r.content)

    try:
        update.message.reply_voice(voice=open(speak_unique, 'rb'))
    except Exception as e:
        update.message.reply_text(text="Falha ao criar mensagem de voz.")

    os.remove(speak_unique)
