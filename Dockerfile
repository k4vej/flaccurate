FROM python:3

WORKDIR /tmp

RUN apt-get update -y
RUN apt-get install -y vim coreutils less sqlite3 python-autopep8

ADD ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY .vim /root/.vim
COPY .vimrc /root/.vimrc

ENV TERM=xterm-256color

WORKDIR /app
