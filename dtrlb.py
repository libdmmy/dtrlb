from telebot import TeleBot
from telebot.types import ChatMemberUpdated, Message

import json
import pathlib
import sys

import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger('dtrlb')

# === CONFIGURATION ===
config_path = pathlib.Path('./config.json')
if not config_path.exists():
    config: dict = {}
    with open(config_path, 'x') as f:
        json.dump({
            'tg_bot_token': 'xxx',
            'tg_superchat_id': 123456789
        }, f, indent=4)
    print('I\'ve just created config.json. Please fill it now.')
    sys.exit(1)
else:
    with open(config_path, 'r') as f:
        config: dict = json.load(f)

def save_config():
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

trusted_users = []
lair_id = config['tg_superchat_id']

# === LOCALIZATION ===
def complete_locale(locale) -> dict:
    for key in ENGLISH_LOCALE.keys():
        if key not in locale.keys():
            locale[key] = ENGLISH_LOCALE[key]

    return locale

ENGLISH_LOCALE = {
    'forum.event_log': 'event log',

    'forum.echo': 'echoes',

    'security.untrusted_user': '⚠️ untrusted user detected ⚠️\n\nI banned him for you. my advice is to reset invite links.\n\nid: `{id}`\nname: `{name}`',

    'generic.starting': 'starting up!',
    'generic.topic_wasnt_found': 'creating {topic} topic for the first time...'
}
RUSSIAN_LOCALE = complete_locale({
    'forum.event_log': 'журнал событий',

    'forum.echo': 'эха',

    'security.untrusted_user': '⚠️ обнаружен неизвестный пользователь ⚠️\n\nвыкинул его из логова за тебя. мой совет таков - сбрось ссылки приглашений.\n\nайди: `{id}`\nимя: `{name}`',

    'generic.starting': 'стартуем!',
    'generic.topic_wasnt_found': 'впервые создаю топик {topic}...'
})
current_locale = RUSSIAN_LOCALE

# === SOME LOGIC IDK ===
def write_into_event_log(text: str):
    bot.send_message(config['tg_superchat_id'], text, parse_mode='Markdown', message_thread_id=config['forums']['event_log'])

def handle_in_forum(codename: str):
    return lambda m: m.message_thread_id == config['forums'][codename]

# === BOT ===
bot = TeleBot(config['tg_bot_token'])

# === POST-CONFIG ===
if 'forums' not in config:
    config['forums'] = {}

def ensure_we_have_following_forum(codename: str, display_name: str):
    if codename not in config['forums']:
        logger.info(current_locale['generic.topic_wasnt_found'].format(topic=codename))
        config['forums'][codename] = bot.create_forum_topic(lair_id, display_name).message_thread_id

# === TOPICS ===

ensure_we_have_following_forum('event_log', current_locale['forum.event_log'])
ensure_we_have_following_forum('echo', current_locale['forum.echo'])

@bot.message_handler(func=handle_in_forum('echo'))
def on_echo_msg(msg: Message):
    bot.reply_to(msg, str(msg.text))

# === SECURITY ===
@bot.chat_member_handler(func=lambda e: e.new_chat_member is not None and e.new_chat_member.status == 'member')
def on_chat_member(event: ChatMemberUpdated):
    if event.new_chat_member.user.id not in trusted_users:
        write_into_event_log(current_locale['security.untrusted_user'].format(id=event.new_chat_member.user.id,
                                                                       name=event.new_chat_member.user.full_name))
        bot.ban_chat_member(lair_id, event.new_chat_member.user.id, until_date=0)

logger.info(current_locale['generic.starting'])
bot.infinity_polling(allowed_updates=['message', 'chat_member'])
save_config()