#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import json
import urllib.request
import os.path

registered_filename = "registered_users.json"
links_filename = "links.json"
lsk_step = 1
lsk_price = 0

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

registered_users = json.load(open(registered_filename, 'r')) if os.path.isfile(registered_filename) else []
links = json.load(open(links_filename, 'r')) if os.path.isfile(links_filename) else []

def update_registered_users():
    with open(registered_filename, 'w') as file:
        json.dump(registered_users, file)

def update_links():
    with open(links_filename, 'w') as file:
        json.dump(links, file)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def lisk_bb(bot, update):
    response = json.loads(urllib.request.urlopen("https://bitbay.net/API/Public/LSKPLN/ticker.json").read().decode("utf-8"))
    update.message.reply_text("Current LSK price is {}.".format(response["last"]))

def register_user(bot, update):
    conversation = str(update.message.chat_id)
    if not conversation in registered_users:
        registered_users.append(conversation)
        update_registered_users()
    update.message.reply_text("You have been registered for LSK price updates! You can unsubscribe at any moment using command /unsubscribe")

def unregister_user(bot, update):
    conversation = str(update.message.chat_id)
    if conversation in registered_users:
        registered_users.remove(conversation)
        update_registered_users()
    update.message.reply_text("You have been unregistered for LSK price updates! You can subscribe back at any moment using command /subscribe")

def remember(bot, update, args):
    node = {
        "user": str(update.message.chat_id),
        "link": args.pop(0),
        "category": args.pop(0),
        "desc": " ".join(args)
    }
    links.append(node)
    update_links()
    update.message.reply_text("Link saved!")

def remind(bot, update, args):
    text = ""
    user = str(update.message.chat_id)
    for node in [node for node in links if node["user"] == user and node["category"] == args[0]]:
        text += node["link"] + "\n" + node["desc"] + "\n\n"
    update.message.reply_text(text)

def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("501827310:AAGgWmr9WR3IKSDsQ9mr0smjvzXIg23j5kE")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("lisk", lisk_bb))
    dp.add_handler(CommandHandler("subscribe", register_user))
    dp.add_handler(CommandHandler("unsubscribe", unregister_user))
    dp.add_handler(CommandHandler("remember", remember, pass_args=True))
    dp.add_handler(CommandHandler("remind", remind, pass_args=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
