# telegram_bot

A Telegram bot written in Python with a variety of commands.
Note: Only works in Python 3!

## Installing dependencies and running

Note: Before start you need to create a telegram bot and get a token, check the oficial documentation here:

https://core.telegram.org/bots

To send images and voice messages this bot uses a proprietary API made by me, this API works by scrapping some webpages and I'm afraid those services would take it down if it went public, maybe it's a silly concern but I will not provide the code for now.

You can message me if you are interested about how this API was developed and I can help.

### Run with Docker (Recommended)

To run this bot using Docker

```
docker build -t telegrambot .

docker run -t --name telegrambot \
              --network telegram-bot-net \  # If the api server is in another container
              -e TELEGRAM_TOKEN='' \
              -e API_SERVER='' \
              telegrambot
```

Note: TELEGRAM_TOKEN='' needs to be replace with your bot token.

API_SERVER='' needs to be configured to use commands **image** and **speak**.

#### Run without Docker

##### Install Dependencies (Only works in Python3)

Create a virtualenv (Optional):
```
mkdir ~/virtualenv
virtualenv -p python3 ~/virtualenv
source ~/virtualenv/bin/activate
```
Install the requirements (use sudo if you are not using a virtualenv):

```pip install -r requirements.txt```

##### Running

After all the requirements are installed.

To run the bot simply execute this commands:
```
export TELEGRAM_TOKEN=<YOUR BOT'S TOKEN> # Configure environment variable
export API_SERVER=<Api server needed for commands image and speak> # Configure environment variable
python bot.py
```

If you have any doubts let me know!
