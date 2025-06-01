from telebot.types import Message
from dtrlb import Plugin

class EchoPlugin(Plugin):
    internal_name = 'echo'
    topic_name = 'echoes'

    def on_my_topic_msg(self, msg):
        self.dtrlb.bot.reply_to(msg, str(msg.text))

class CalcPlugin(Plugin):
    internal_name = 'calc'
    topic_name = 'calculator'

    def on_my_topic_msg(self, msg: Message):
        text = str(msg.text)

        # https://stackoverflow.com/a/64471342
        allowed_chars = "0123456789+-*(). /"
        for char in text:
            if char not in allowed_chars:
                raise Exception(f'are you trying to hack me? "{char}" is disallowed')

        result = eval(text)
        self.dtrlb.bot.reply_to(msg, f'{msg.text}={result}')