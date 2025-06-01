from abc import ABC
import logging

import telebot

class Plugin(ABC):
    internal_name: str
    topic_name: str
    dtrlb: 'DTRLB'

    def __init__(self) -> None:
        pass

    def on_pre_add(self) -> None:
        pass

    def on_post_add(self) -> None:
        pass

class DTRLB():
    bot: telebot.TeleBot
    plugins: list[Plugin] = []

    def __init__(self, token: str, plugins: list[Plugin]=[]) -> None:
        self.bot = telebot.TeleBot(token=token)
        self.add_plugin(*plugins)

    def setup_logging(self) -> None:
        import sys
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    def add_plugin(self, *plugins: Plugin) -> None:
        for plugin in plugins:
            if self.has_plugin(plugin.internal_name):
                self.warn(f'{plugin.internal_name} is already added. skipped')
                continue

            plugin.dtrlb = self
            plugin.on_pre_add()
            self.plugins.append(plugin)
            plugin.on_post_add()

    def has_plugin(self, plugin_name: str) -> bool:
        for plugin in self.plugins:
            if plugin.internal_name == plugin_name:
                return True
        return False

    def log(self, obj: object) -> None:
        logging.info(obj)

    def warn(self, obj: object) -> None:
        logging.warning(obj)

    def launch(self) -> None:
        self.log('Starting up!')
        self.bot.infinity_polling()