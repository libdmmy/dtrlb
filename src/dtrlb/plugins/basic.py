from telebot.types import Message, ChatMemberUpdated, ChatMember
from dtrlb import Plugin

# TOPICS
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

class SecurityPlugin(Plugin):
    internal_name = 'security'

    trusted_users: list[int]

    def __init__(self, trusted_users: list[int]) -> None:
        self.trusted_users = trusted_users
        super().__init__()

    def on_add(self) -> None:
        super().on_add()

        @self.dtrlb.bot.chat_member_handler()
        def _(event: ChatMemberUpdated):
            if event.new_chat_member is not None:
                self.on_new_member(event.new_chat_member)

    def on_new_member(self, member: ChatMember):
        id = member.user.id
        if id != self.dtrlb.bot.bot_id and id not in self.trusted_users:
            self.logger.warning('unknown user has entered chat! attempting to ban...')
            self.dtrlb.bot.ban_chat_member(self.dtrlb.chat_id, id, 0)
            self.dtrlb.send_to_event_log(f'⚠️ unknown user (`{id}`) has entered the chat ⚠️\nI recommend you resetting invite links!')

class EventLogPlugin(Plugin):
    internal_name = 'event_log'
    topic_name = 'event log'

    def on_add(self) -> None:
        super().on_add()
        self.dtrlb.event_log_instance = self