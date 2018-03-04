#!/usr/bin/env python3

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

logger = logging.getLogger('telegram')
logger.setLevel(logging.INFO)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    from server.meat import games_manipulator

    update.message.reply_text('Hi! Number of active games: %s' % len(games_manipulator.runningGames))


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(bot, update):
    """Echo the user message."""
    logger.info('Received message: {}'.format(update))
    update.message.reply_text(update.message.text)


def game(bot, update):
    logger.info("Game request: {}".format(update))
    bot.answer_callback_query(update.callback_query.id, url='https://playhive.club')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def create_bot(telegram_token):
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(telegram_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CallbackQueryHandler(game))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    return updater
