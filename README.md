# telegram_bot

A Telegram bot written in Python with a variety of commands.
Note: Only works in Python 3!

Dependencies

Python Telegram Bot (https://github.com/python-telegram-bot/python-telegram-bot):
To install in Debian based distributions:
sudo pip3 install python-telegram-bot

Fortune (http://linux.die.net/man/6/fortune):
To install in Debian based distributions:
sudo apt-get install fortune

requests (http://docs.python-requests.org/en/latest/):
sudo pip3 install requests

botan.io (https://github.com/botanio/sdk/):
It's added as a git submodule, just run: git submodule init && git submodule update

Before you can start the bot you need to create a telegram bot and get a token, check the oficial documentation here:
https://core.telegram.org/bots

After all the requirements are installed you can run the bot using the command:
python3 telebot.py

Theres a script to keep the bot running "forever", you can run it with ./run_forever.sh

If you have any doubts let me know!
