from abc import ABC
import logging
from pathlib import Path
import json

import telebot
from telebot.types import Message

class Plugin(ABC):
    internal_name: str
    topic_name: str
    topic_id: int
    dtrlb: 'DTRLB'
    config: dict = {}

    def __init__(self) -> None:
        pass    

    def on_add(self) -> None:
        with open(self.get_config_file_path(), 'r') as f:
            self.config = json.load(f)

        self._refresh_topic_id()

    def on_msg(self, msg: Message) -> None:
        if msg.message_thread_id == self.topic_id:
            self.on_my_topic_msg(msg)

    def on_my_topic_msg(self, msg: Message) -> None:
        pass
 
    def get_my_directory(self) -> Path:
        path = self.dtrlb.plugins_directory / f'{self.internal_name}'
        path.mkdir(exist_ok=True)

        return path
    
    def _refresh_topic_id(self):
        id = self.config.get('topic_id', 0)

        if id == 0:
            self.dtrlb.log(f'{self.internal_name}\'s topic wasn\'t found. creating new one')
            topic = self.dtrlb.bot.create_forum_topic(self.dtrlb.chat_id, self.topic_name)
            id = topic.message_thread_id
            self.config['topic_id'] = id
            self.save_config()

        self.topic_id = id
    
    def get_config_file_path(self) -> Path:
        path = self.get_my_directory() / 'config.json'
        if not path.exists():
            with open(path, 'x') as f:
                f.write('{}')

        return path

    def save_config(self) -> None:
        with open(self.get_config_file_path(), 'w') as f:
            json.dump(self.config, f, indent=2)

class DTRLB():
    bot: telebot.TeleBot
    chat_id: int

    plugins: list[Plugin] = []
    working_directory: Path = Path('.')
    plugins_directory: Path = Path('./plugins')

    config: dict = {}

    def __init__(self, plugins: list[Plugin]=[]):
        self.setup_logging()

        with open(self.get_config_file_path(), 'r') as f:
            self.config = json.load(f)

        self._ensure_we_have_chat_id()

        self.bot = telebot.TeleBot(token=self.get_token())
        self.add_plugin(*plugins)
        self.plugins_directory.mkdir(exist_ok=True)

        @self.bot.message_handler(func=lambda m: True)
        def _(msg: Message):
            self.on_msg(msg)

    def setup_logging(self):
        import sys
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    def add_plugin(self, *plugins: Plugin):
        for plugin in plugins:
            if self.has_plugin(plugin.internal_name):
                self.warn(f'{plugin.internal_name} is already added. skipped')
                continue

            plugin.dtrlb = self
            plugin.on_add()
            self.plugins.append(plugin)

    def has_plugin(self, plugin_name: str) -> bool:
        for plugin in self.plugins:
            if plugin.internal_name == plugin_name:
                return True
        return False
    
    def on_msg(self, msg: Message):
        for plugin in self.plugins:
            try:
                plugin.on_msg(msg)
            except BaseException as e:
                text = f'{e.__class__.__name__}: {str(e)}'
                self.warn(text)
                self.bot.reply_to(msg, f'got exception, while handling your message 🫠:\n```exception\n{text}```', parse_mode='MarkdownV2')

    def log(self, obj: object):
        logging.info(obj)

    def warn(self, obj: object):
        logging.warning(obj)

    def launch(self):
        self.log('Starting up!')
        self.bot.infinity_polling()
        self.on_terminate()

    def on_terminate(self):
        self.save_config()
        for plugin in self.plugins:
            plugin.save_config()

    def get_config_file_path(self) -> Path:
        path = self.working_directory / 'config.json'
        path.touch(exist_ok=True)
        return path

    def save_config(self) -> None:
        with open(self.get_config_file_path(), 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_token(self) -> str:
        token = self.config.get('tg_bot_token', '')
        if token == '':
            while True:
                token = input('enter your tg bot token: ')
                if token.strip() != '':
                    break
            self.config['tg_bot_token'] = token
            self.save_config()

        return token
    
    def _ensure_we_have_chat_id(self):
        id = self.config.get('chat_id', 0)
        if id == 0:
            while True:
                id = int(input('enter your chat\'s id (-1001234567890): '))
                if id != 0:
                    break

            self.config['chat_id'] = id
            self.save_config()
        self.chat_id = id