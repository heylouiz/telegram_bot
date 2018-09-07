#!/usr/bin/env python
import os
import requests
import random

import telegram

command_name = "image"

need_parameters = True

ask_for_parameters_text = "O que você quer buscar?"


def help():
    return '/image - Busca e manda uma imagem aleatória.\n - Uso: /image frase\n' +\
           'Use -best para obter a melhor imagem da busca.\n - Uso: /image frase -best\n'


def custom_search(query):
    r = requests.get("{}/image/{}".format(os.environ['API_SERVER'], query))
    if r.status_code == 200:
        return r.json()
    return []


@telegram.ext.dispatcher.run_async
def process_command(bot, update, args, user_data):
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
        update.message.reply_text("Não encontrei nenhum resultado para a busca.")
        return

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
                update.message.reply_text("Falha ao enviar imagens para a busta.")
                return
            continue
