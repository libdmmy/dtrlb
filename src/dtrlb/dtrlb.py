import telebot
import logging

class DTRLB():
    bot: telebot.TeleBot

    def __init__(self, token: str) -> None:
        self.bot = telebot.TeleBot(token=token)

    def setup_logging(self) -> None:
        import sys
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    def log(self, obj: object) -> None:
        logging.info(obj)

    def launch(self) -> None:
        self.log('Starting up!')
        self.bot.infinity_polling()