from telebot import TeleBot
from telebot.types import ChatMemberUpdated, Message, InputMediaPhoto, LinkPreviewOptions

import os
import json
import pathlib
import sys

#from pprint import pprint

import ydl

import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger('dtrlb')

pathlib.Path('./temp').mkdir(exist_ok=True)

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
    'forum.calc': 'calculator',
    'forum.calc.invalid_char': 'invalid character: `{char}`. allowed ones are `0123456789 +-*/`',

    'forum.yt-dlp': 'yt-dlp',

    'security.untrusted_user': '⚠️ untrusted user detected ⚠️\n\nI banned him for you. my advice is to reset invite links.\n\nid: `{id}`\nname: `{name}`',

    'generic.starting': 'starting up!',
    'generic.topic_wasnt_found': 'creating {topic} topic for the first time...'
}
RUSSIAN_LOCALE = complete_locale({
    'forum.event_log': 'журнал событий',

    'forum.echo': 'эха',
    'forum.calc': 'калькулятор',
    'forum.calc.invalid_char': 'данный символ запрещён: `{char}`. разрешены только `0123456789 +-*/`',

    'security.untrusted_user': '⚠️ обнаружен неизвестный пользователь ⚠️\n\nвыкинул его из логова за тебя. мой совет таков - сбрось ссылки приглашений.\n\nайди: `{id}`\nимя: `{name}`',

    'generic.starting': 'стартуем!',
    'generic.topic_wasnt_found': 'впервые создаю топик {topic}...'
})
current_locale = RUSSIAN_LOCALE

# === SOME LOGIC IDK ===
def write_into_event_log(text: str):
    bot.send_message(lair_id, text, parse_mode='Markdown', message_thread_id=config['forums']['event_log'])

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
        save_config()

# === TOPICS ===
ensure_we_have_following_forum('event_log', current_locale['forum.event_log'])
ensure_we_have_following_forum('echo', current_locale['forum.echo'])
ensure_we_have_following_forum('calc', current_locale['forum.calc'])
ensure_we_have_following_forum('yt-dlp', current_locale['forum.yt-dlp'])

# === BASIC ===
@bot.message_handler(func=handle_in_forum('echo'))
def on_echo_msg(msg: Message):
    bot.reply_to(msg, str(msg.text))

@bot.message_handler(func=handle_in_forum('calc'))
def on_calc_msg(msg: Message):
    for c in str(msg.text):
        if c not in '0123456789 +-*/':
            bot.reply_to(msg, current_locale['forum.calc.invalid_char'].format(char=c), parse_mode='Markdown')
            return
    
    try:
        bot.reply_to(msg, eval(str(msg.text)))
    except Exception as e:
        bot.reply_to(msg, f'`{e.__class__.__name__}: {e}`', parse_mode='Markdown')

# === DOWNLOADERS ===
@bot.message_handler(func=handle_in_forum('yt-dlp'))
def on_ytdlp_msg(msg: Message):
    progress_msg = bot.reply_to(msg, 'fetching information...')

    info = ydl.get_information(url=str(msg.text))

    title = info['title']
    thumbnail = info['thumbnail']
    url = info['webpage_url']
    duration = info['duration']
    duration_str = info['duration_string']

    width = info['width']
    height = info['height']

    channel = info['channel']
    channel_url = info['channel_url']

    info_string = f'<strong>{title}</strong> <a href="{url}">🔗</a>\n' + \
                  f'by #{channel.replace(' ', '_')} <a href="{channel_url}">🔗</a>'
    
    status_string = f'\n\n<em>downloading...</em>'

    bot.edit_message_media(message_id=progress_msg.id,
                           chat_id=lair_id,
                           media=InputMediaPhoto(thumbnail,
                                                 caption=info_string + status_string,
                                                 parse_mode='HTML'))
    
    video_path = ydl.download(info)

    status_string = f'\n\n<em>uploading...</em>'

    bot.edit_message_media(message_id=progress_msg.id,
                           chat_id=lair_id,
                           media=InputMediaPhoto(thumbnail,
                                                 caption=info_string + status_string,
                                                 parse_mode='HTML'))

    with open(video_path, 'rb') as f:
        bot.send_video(lair_id, f,
                       width=width, height=height,
                       thumbnail=thumbnail,
                       message_thread_id=config['forums']['yt-dlp'])

    os.remove(video_path)
    bot.delete_message(lair_id, msg.id)

# === SECURITY ===
@bot.chat_member_handler(func=lambda e: e.new_chat_member is not None and e.new_chat_member.status == 'member'
                         and e.new_chat_member.user.id != bot.user.id)
def on_chat_member(event: ChatMemberUpdated):
    if event.new_chat_member.user.id not in trusted_users:
        write_into_event_log(current_locale['security.untrusted_user'].format(id=event.new_chat_member.user.id,
                                                                       name=event.new_chat_member.user.full_name))
        bot.ban_chat_member(lair_id, event.new_chat_member.user.id, until_date=0)

logger.info(current_locale['generic.starting'])
bot.infinity_polling(allowed_updates=['message', 'chat_member'])
save_config()