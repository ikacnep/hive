#!/usr/bin/env python3

import logging
import logging.handlers
import os
import signal

from server import meat, telegram_bot


logger = logging.getLogger('hive.launcher')

logging_settings = {
    'werkzeug': (logging.INFO, 'webserver.log'),
    'hive.launcher': (logging.DEBUG, 'launch.log'),
    'hive.telegram': (logging.DEBUG, 'telegram_bot.log'),
    'hive.meat': (logging.DEBUG, 'meat.log'),
}


def stop_and_quit(*unused_args):
    # Фласк не даёт нормального интерфейса для остановки, а бот не останавливается
    os._exit(1)


def setup_signals():
    signal.signal(signal.SIGTERM, stop_and_quit)
    signal.signal(signal.SIGINT, stop_and_quit)


def setup_logging():
    log_directory = os.path.join('work', 'log')
    os.makedirs(log_directory, 0o755, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def create_handler(filename):
        return logging.handlers.TimedRotatingFileHandler(
            filename=os.path.join(log_directory, filename),
            when='d',
            interval=1,
            backupCount=20,
        )

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[create_handler('everything.log')],
    )

    for logger_name, settings in logging_settings.items():
        level, filename = settings

        logger.debug('Logging {} to {} on {}'.format(logger_name, filename, level))

        other_logger = logging.getLogger(logger_name)

        other_logger.setLevel(level)

        handler = create_handler(filename)
        handler.setFormatter(formatter)

        other_logger.addHandler(handler)


def main():
    setup_signals()
    setup_logging()

    logger.info('Starting up')

    try:
        telegram_token = open('conf/telegram.bot.token').read().strip()
    except:
        logger.exception('Cannot read bot token, not launching bot')
    else:
        logger.debug('Launching bot')
        telegram_bot.HiveTelegramBot(telegram_token)

    logger.debug('Launching meat')

    meat.start(
        tls_cert='conf/fullchain.pem',
        tls_key='conf/privkey.pem',
        secret_key='conf/secret_key.txt',
        use_reloader=False,
    )


if __name__ == '__main__':
    main()