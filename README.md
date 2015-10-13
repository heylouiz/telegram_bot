# telegram_bot

A Telegram bot with a variety of commands

This bot uses the "Python Telegram Bot", you need to install it to make the bot work.
Link to the project:
https://github.com/leandrotoledo/python-telegram-bot

Other requirements:
Fortune (http://linux.die.net/man/6/fortune):
sudo apt-get install fortune

Imagemagick (http://www.imagemagick.org):
sudo apt-get install imagemagick

dota2py (https://github.com/andrewsnowden/dota2py):
pip install dota2py

simplejson (https://pypi.python.org/pypi/simplejson):
sudo apt-get install python-simplejson

Before you can start the bot you need to create a telegram bot and get a token, check the oficial documentation here:
https://core.telegram.org/bots

This project uses a command to get the match history of a Dota 2 Player (not working correctly) and needs a Steam API Key, you can get one here:
http://steamcommunity.com/dev/apikey

After all the requirements are installed you can run the bot using the command:
python main.py

Theres a script to keep the bot running "forever", you can run it with ./run_forever.sh

If you have any doubts let me know!
