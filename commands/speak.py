#!/usr/bin/env python
import os
import random
import requests
import tempfile
from langcodes import standardize_tag

from urllib.parse import quote
from telegram.ext.dispatcher import run_async

from google.cloud import texttospeech


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "api_key.json"

# Select the type of audio file
audio_config = texttospeech.types.AudioConfig(
    audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16
)

# Instantiate Google TTS client
client = texttospeech.TextToSpeechClient()


def help():


def generate_audio(sentence, language, gender=None):
    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=sentence)

    if not gender:
        gender = "SSML_VOICE_GENDER_UNSPECIFIED"
    elif 'w' in gender:
        gender = "FEMALE"
    else:
        gender = "MALE"

    # Get available voices
    voices = client.list_voices()
    BCP47lang = standardize_tag(language)
    voices2 = client.list_voices(BCP47lang)
    selectedVoices = [
        voice.name
        for voice in voices.voices
        if (BCP47lang in voice.language_codes and "Standard" not in voice.name)
    ]
    selectedVoice = random.choice(selectedVoices)

    # Build the voice request, select the language code and the ssml
    voice = texttospeech.types.VoiceSelectionParams(
        name=selectedVoice,
        language_code=selectedVoice[:5],  # BCP-47 tag
        ssml_gender=getattr(texttospeech.enums.SsmlVoiceGender, gender)
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    return response


@run_async
def original_speak(update, context):
    if hasattr(update.message, 'text') and "-help" in update.message.text:
        update.message.reply_text(help())
        return

    # Default is pt-br
    engine = "3"
    lang = "6"  # Portuguese
    voice = "2"  # Rafael

    args = context.args
    if not args and update.message.reply_to_message:
        args = update.message.reply_to_message.text.split(" ")

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
            engine = "3"
            voice = "1"  # Helena
        args.pop(args.index("-w"))

    text_to_speech = " ".join(args)

    if not text_to_speech:
        update.message.reply_text('Nada pra falar, coloque a frase a ser'
                                  ' falada na frente do comando "/speak cachorro quente"')
        return

    # Make speech url
    text_to_speech = quote(text_to_speech)
    url = f'{BASE_URL}/{engine}/{lang}/{voice}/{text_to_speech}'
    try:
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            raise requests.exceptions.RequestException
    except requests.exceptions.RequestException:
        update.message.reply_text(text="Falha ao criar mensagem de voz.",
                                  reply_to_message_id=update.message.message_id)
        return

    try:
        update.message.reply_voice(voice=r.raw)
    except Exception:
        update.message.reply_text(text="Falha ao criar mensagem de voz.")


@run_async
def speak(update, context):
    if hasattr(update.message, 'text') and "-help" in update.message.text:
        update.message.reply_text(help())
        return

    lang = "pt-BR"
    gender = None

    args = context.args
    if not args and update.message.reply_to_message:
        args = update.message.reply_to_message.text.split(" ")

    text_to_speech = " ".join(args)
    # print(text_to_speech)

    if not text_to_speech:
        update.message.reply_text('Nada pra falar, coloque a frase a ser'
                                  ' falada na frente do comando, ex.: "/speak cachorro quente"')
        return

    try:
        wavenetResponse = generate_audio(text_to_speech, lang, gender)
    except Exception as e:
        update.message.reply_text(text="Falha ao criar mensagem de voz.", reply_to_message_id=update.message.message_id)
        print(e)
        return original_speak(update, context)


    try:
        update.message.reply_voice(voice=wavenetResponse.audio_content)
    except Exception as e:
        update.message.reply_text(text="Falha ao criar mensagem de voz.")
        print(e)
        return original_speak(update, context)
