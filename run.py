#!/usr/bin/env python3

import logging
import os
import signal

from server import meat, telegram_bot


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot = telegram_bot.create_bot(open('conf/telegram.bot.token').read().strip())


def stop_and_quit(*unused_args):
    # Фласк не даёт нормального интерфейса для остановки, а бот не останавливается
    os._exit(1)


signal.signal(signal.SIGTERM, stop_and_quit)
signal.signal(signal.SIGINT, stop_and_quit)


meat.start(
    tls_cert='conf/fullchain.pem',
    tls_key='conf/privkey.pem',
    secret_key='conf/secret_key.txt',
    use_reloader=False,
)
