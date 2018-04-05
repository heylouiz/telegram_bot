FROM alpine

RUN apk --update --no-cache add \
    python3 \
    fortune

WORKDIR /app

ADD . /app

RUN pip3 install -U pip
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

CMD ["python3", "bot.py"]

