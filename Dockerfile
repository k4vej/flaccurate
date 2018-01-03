FROM python:3

WORKDIR /tmp

RUN apt-get update -y
RUN apt-get install -y git ncurses-dev coreutils less
RUN git clone https://github.com/vim/vim.git && cd vim && ./configure && make && make install

ADD ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY .vim /root/.vim
COPY .vimrc /root/.vimrc

WORKDIR /app
