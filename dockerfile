FROM python:latest
MAINTAINER https://medium.com/@a29988122

RUN pip install youtube-dl
RUN pip install telegram
RUN pip install python-telegram-bot
RUN pip install requests
RUN pip install configparser
RUN pip install dropbox

WORKDIR /home

COPY ./AwwExpress_bot.py /home
COPY ./config.ini /home

CMD python AwwExpress_bot.py
