#!/usr/bin/env python3

import json
import logging
import os
import textwrap

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from server.meat import games_manipulator


logger = logging.getLogger('telegram')
logger.setLevel(logging.INFO)


class HiveTelegramBot:
    _inline_message_id_to_lobby = {}

    def __init__(self, token):
        # Create the EventHandler and pass it your bot's token.
        updater = Updater(token)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(CommandHandler("reload", self.reload))

        dp.add_handler(CallbackQueryHandler(self.game))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, self.echo))

        # log all errors
        dp.add_error_handler(self.error)

        # Start the Bot
        updater.start_polling()

    @staticmethod
    def pick_user_name(update):
        user = update.from_user

        if user.username:
            return user.username

        name = user.first_name

        if user.last_name:
            name += ' ' + user.last_name

        return name

    def choose_player_from_message(self, message):
        return games_manipulator.GetOrCreatePlayer(
            name=self.pick_user_name(message),
            telegramId=message.from_user.id
        ).player

    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        self.log_update('/start request', update)

        bot.send_game(
            chat_id=update.message.chat.id,
            game_short_name='PlayHive',
        )

    def help(self, bot, update):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')

    def echo(self, bot, update):
        """Echo the user message."""
        logger.info('Received message: {}'.format(update))
        update.message.reply_text(update.message.text)

    def reload(self, bot, update):
        """ Reload everything, done externally in ~/prod.sh """
        update.message.reply_text("'kay")
        os._exit(42)

    def game(self, bot, update):
        self.log_update('Launch game', update)

        inline_message_id = update.callback_query.inline_message_id

        player = self.choose_player_from_message(update.callback_query)

        if inline_message_id in self._inline_message_id_to_lobby:
            lobby_id = self._inline_message_id_to_lobby[inline_message_id]

            try:
                games_manipulator.GetLobby(lobby_id=lobby_id)
            except:
                del self._inline_message_id_to_lobby[inline_message_id]
        else:
            lobby_id = games_manipulator.CreateLobby(name=player.name, player=player.id).id

            self._inline_message_id_to_lobby[inline_message_id] = lobby_id

        url = 'https://playhive.club/lobby/{}?telegramId={}'.format(lobby_id, player.telegramId)

        logger.info('Answering with url: {}'.format(url))

        bot.answer_callback_query(update.callback_query.id, url=url)

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    @staticmethod
    def log_update(prefix, update):
        logger.info("{}: {}".format(prefix, json.dumps(update.to_dict(), indent=4, ensure_ascii=False)))
