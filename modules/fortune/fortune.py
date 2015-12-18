import subprocess
from telegram import ChatAction
from telegram.dispatcher import run_async

def help_command():
    return '/fortune - Print a fortune message.\n - Usage: /fortune\n'

@run_async
def fortune_command(bot, update):
    message = update.message.text
    message = message.replace("/fortune", "").strip()

    if message.find("-help") >= 0:
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id, text=help_command())
        return

    # Inform that the bot will send a text message
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    database = "-a"
    lang = "en "
    print(message)
    if message.find("-pt") > 0:
        database = "/usr/share/games/fortunes/brasil"
        lang = ""

    fortune_out = subprocess.Popen("fortune " + database, stdout=subprocess.PIPE, shell=True)
    output = fortune_out.communicate()[0]

    fortune_message = output.decode("utf-8")

    bot.sendMessage(chat_id=update.message.chat_id, text=fortune_message)
