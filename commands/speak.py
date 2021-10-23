#!/usr/bin/env python

import logging
import os
import random
import argparse
from enum import Enum

import requests
from langcodes import standardize_tag
from urllib.parse import quote
from telegram.ext.dispatcher import run_async
from google.cloud import texttospeech

speak_logger = logging.getLogger(__name__)
speak_logger.setLevel(logging.DEBUG)


parser = argparse.ArgumentParser()
parser.add_argument("-w", action="store_true", default=None)
parser.add_argument("-m", action="store_true", default=None)
parser.add_argument("-en", action="store_true", default=None)
parser.add_argument("-l", default="pt-BR")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "api_key.json"
GCP_TTS_CHAR_LIMIT = 22


# Instantiate Google TTS client
client = texttospeech.TextToSpeechClient()

# Select the type of audio file
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16
)


class SsmlVoiceGender(Enum):
    SSML_VOICE_GENDER_UNSPECIFIED = 0
    MALE = 1
    FEMALE = 2
    NEUTRAL = 3


def help():
    return (
        "/speak - Manda uma mensagem de voz com o texto.\n*Uso*: /speak texto\n"
        + 'Para falar em inglês, escreva também o parâmetro "-l". Uso: /speak -l en-US text in english.\n'
        + "Isto vale para quase qualquer idioma, utilizando o padrão [BCP-47](https://en.wikipedia.org/wiki/IETF_language_tag).\n"
        + "\nO gênero da voz é aleatório por padrão:\n"
        + 'Para usar uma voz masculina, utilize o parâmetro "-m". Uso: /speak -m texto.\n'
        + 'Para usar uma voz feminina, utilize o parâmetro "-w".\n'
        + "\nOs parâmetros podem ser colocados em qualquer lugar da mensagem."
    )


def wavenet_speak(update, context, sentence, language, gender=None):
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=sentence)

    # if not gender:
    #     gender = "SSML_VOICE_GENDER_UNSPECIFIED"
    if gender and "w" in gender:
        gender = "FEMALE"
    else:
        gender = "MALE"

    # Get available voices
    voices = client.list_voices()
    bcp47_lang = standardize_tag(language)

    selectedVoices = [
        voice.name
        for voice in voices.voices
        if (
            str(voice.ssml_gender) == str(SsmlVoiceGender[gender])
            and bcp47_lang in voice.language_codes
            and "Standard" not in voice.name
        )
    ]

    try:
        selectedVoice = random.choice(selectedVoices)
    except Exception as e:
        speak_logger.debug("Falha ao criar mensagem de voz com WaveNet."),
        speak_logger.warning(e)
        speak_logger.debug("Defaulting to standard TTS...")
        return


    # Build the voice request, select the language code and the ssml
    voice = texttospeech.VoiceSelectionParams(
        name=selectedVoice,
        language_code=selectedVoice[:5],  # BCP-47 tag
        # ssml_gender=getattr(texttospeech.SsmlVoiceGender, gender)  # Apparently redundant
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        request={"input": synthesis_input, "voice": voice, "audio_config": audio_config}
    )

    return response


def send_original_speak(update, context):
    # Default is pt-br
    engine = "3"
    lang = "6"  # Portuguese
    voice = "2"  # Rafael

    args_lang = "pt-BR"

    args = context.args
    args, unknown_args = parser.parse_known_args(args)
    args_lang = args.l

    reply_id = update.message.message_id
    if update.message.reply_to_message:
        text_to_speech = update.message.reply_to_message.text
        reply_id = update.message.reply_to_message.message_id
    else:
        text_to_speech = " ".join(unknown_args)

    if args.w:
        if args.en:
            voice = "6"  # Ashley
            lang = "1"  # English
        else:
            voice = "1"  # Helena
    else:
        if args.en:
            engine = "4"
            voice = "5"  # Daniel
            lang = "1"  # English

    if not text_to_speech:
        update.message.reply_text(
            'Nada a se falar, coloque a frase a ser falada após o comando, ex.: "/speak cachorro quente"'
        )
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
    if hasattr(update.message, "text") and "-help" in update.message.text:
        update.message.reply_text(
            help(),
            parse_mode="markdown",
            disable_web_page_preview=True,
        )
        return

    lang = "pt-BR"
    gender = None

    args = context.args

    args, unknown_args = parser.parse_known_args(args)
    text_to_speech = " ".join(unknown_args)

    lang = args.l
    if args.w:
        gender = "w"
    elif args.m:
        gender = "m"

    reply_id = update.message.message_id
    if update.message.reply_to_message:
        text_to_speech = update.message.reply_to_message.text
        reply_id = update.message.reply_to_message.message_id

    if not text_to_speech:
        update.message.reply_text(
            'Nada a se falar, coloque a frase a ser falada após o comando, ex.: "/speak cachorro quente"'
        )
        return

    try:
        if len(text_to_speech.strip()) <= GCP_TTS_CHAR_LIMIT:
            wavenet_response = wavenet_speak(update, context, text_to_speech.strip()[:GCP_TTS_CHAR_LIMIT], lang, gender)
        else:
            raise ValueError(f"String is longer than {GCP_TTS_CHAR_LIMIT}.")

        try:
            return update.message.reply_voice(
                voice=wavenet_response.audio_content, reply_to_message_id=reply_id
            )
        except Exception as e:
            speak_logger.debug("Falha ao criar mensagem de voz com WaveNet."),
            speak_logger.warning(e)
            return send_original_speak(update, context)
    except Exception as e:
        speak_logger.debug("Falha ao criar mensagem de voz com WaveNet."),
        speak_logger.warning(e)
        return send_original_speak(update, context)
