from telebot import TeleBot
from telebot.types import ChatMemberUpdated

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
ENGLISH_LOCALE = {
    'forum.event_log': 'event log',

    'forum.echo': 'echoes',

    'generic.starting': 'starting up!'
}
RUSSIAN_LOCALE = {
    'forum.event_log': 'журнал событий',

    'forum.echo': 'эха',

    'generic.starting': 'стартуем!'
}
current_locale = RUSSIAN_LOCALE

# === SOME LOGIC IDK ===
def write_into_event_log(text: str):
    pass

# === BOT ===
bot = TeleBot(config['tg_bot_token'])

@bot.chat_member_handler()
def on_chat_member(event: ChatMemberUpdated):
    if event.new_chat_member is None:
        return
    
    if event.new_chat_member.user.id not in trusted_users:
        bot.ban_chat_member(lair_id, event.new_chat_member.user.id, until_date=0)

# === POST-CONFIG ===
if 'forums' not in config:
    config['forums'] = {}

def ensure_we_have_following_forum(codename: str, display_name: str):
    if codename not in config['forums']:
        config['forums'][codename] = bot.create_forum_topic(lair_id, display_name).message_thread_id

ensure_we_have_following_forum('event_log', current_locale['forum.event_log'])
ensure_we_have_following_forum('echo', current_locale['forum.echo'])

logger.info(current_locale['generic.starting'])
bot.infinity_polling(allowed_updates=['message', 'chat_member'])
save_config()