# telegram_bot

A Telegram bot written in Python with a variety of commands.
Note: Only works in Python 3!

## Installing dependencies and running

Note: Before start you need to create a telegram bot and get a token, check the oficial documentation here:
https://core.telegram.org/bots

### Dependencies (Only works in Python3)

Create a virtualenv (Optional):
```
mkdir ~/virtualenv
virtualenv -p python3 ~/virtualenv
source ~/virtualenv/bin/activate
```
Install the requirements (use sudo if you are not using a virtualenv):

```pip install -r requirements.txt```

### Running


After all the requirements are installed edit config.json file with your BOT's Token.

To run the bot simply execute this command:
```python bot.py```

Theres a script to keep the bot running "forever", you can run it with ```./run_forever.sh```

If you have any doubts let me know!
