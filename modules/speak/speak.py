import os
import requests
import calendar
import time
from xml.etree.ElementTree import Element, tostring
from hashlib import md5
from urllib.parse import urlencode
from telegram import ChatAction
from telegram.dispatcher import run_async

BASE_URL = 'http://cache-a.oddcast.com/c_fs/'

def xml_elem_str(name, text):
    el = Element(name)
    el.text = text
    return tostring(el)

def tts_url(text, engine=None, lang=None, voice=None):

    prologue = b''.join(xml_elem_str(n, t) for n, t in (
        ('engineID', str(engine)),
        ('voiceID',  str(voice)),
        ('langID',   str(lang)),
        ('ext', 'mp3'),
    ))

    hash = md5(prologue + text.encode()).hexdigest()

    url = BASE_URL + hash + '.' + 'mp3' + '?' + urlencode({
        'engine': engine,
        'language': lang,
        'voice': voice,
        'useUTF8': 1,  # is this needed?
        'text': text,
    })

    return url

def help_command():
    return '/speak - Make the bot speak.\n- Usage: /speak text\n' +\
           'By default the bot speaks portuguese, use the parameter "-en"' +\
           'to make it speak in english.\n- Usage: /speak -en text'

@run_async
def speak_command(bot, update):
    message = update.message.text
    message = message.split(' ', 1)[1].strip()

    if message.find("-help") >= 0:
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id, text=help_command())
        return

    # Inform that the bot will send an audio file
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_AUDIO)

    lang_arg = message.split(" ")[0]

    if lang_arg == "-en":
        message = message.replace("en", "", 1).strip() # Remove lang arg from message
        engine = 4
        voice = 5 # Daniel
        lang = 1
    else: # default is pt-br
        engine = 2
        voice = 5 # Felipe
        lang = 6

    speak_unique = 'speak' + str(calendar.timegm(time.gmtime())) + '.mp3'

    url = tts_url(text=message, engine=engine, lang=lang, voice=voice)

    r_file = requests.get(url)

    with open(speak_unique, 'wb') as speak_file:
        speak_file.write(r_file.content)

    try:
        bot.sendVoice(chat_id=update.message.chat_id, voice=open(speak_unique, 'rb'))
    except Exception as e:
        print("sendVoice Error: " + str(e))
        bot.sendMessage(chat_id=update.message.chat_id, text='Failed to speak, try again')

    os.remove(speak_unique)

