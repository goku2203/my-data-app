import re
import os
from os import environ
from time import time
from Script import script

# Regex pattern for checking integer IDs
id_pattern = re.compile(r'^[-+]?\d+$')

def is_enabled(value, default):
    if not value:
        return default
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    return default

# --- Bot Credentials ---
BOT_USERNAME = environ.get("BOT_USERNAME", "Mikasa_Lovely_bot")
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ.get('API_ID', '28910807'))
API_HASH = environ.get('API_HASH', 'ed988261e49d480ef468664ce8c2eff0')
BOT_TOKEN = environ.get('BOT_TOKEN', '')

# --- Keep Alive ---
KEEP_ALIVE_URL = environ.get("KEEP_ALIVE_URL", "https://burning-brittney-leech2-3bc21fb5.koyeb.app/")

# --- Modes & Settings ---
HYPER_MODE = is_enabled(environ.get('HYPER_MODE', 'False'), False)
REQUEST_FSUB_MODE = is_enabled(environ.get('REQUEST_FSUB_MODE', 'True'), True)
BOT_START_TIME = time()
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = is_enabled(environ.get('USE_CAPTION_FILTER', 'False'), False)

PICS = environ.get('PICS', 'https://i.ibb.co/p6SmhYv3/photo.jpg https://i.ibb.co/k6M0CyGs/photo.jpg https://i.ibb.co/JRDZjtwT/photo.jpg https://i.ibb.co/prB7zBV0/photo.jpg https://i.ibb.co/SDjyjk4M/photo.jpg https://i.ibb.co/mFbGL4yW/photo.jpg https://i.ibb.co/23TMfwyF/photo.jpg').split()

# --- Admins, Channels & Users ---
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '600302393').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []

auth_grp = environ.get('AUTH_GROUPS', '')
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
DEFAULT_AUTH_CHANNELS = [int(x) for x in environ.get("AUTH_CHANNEL", '').split() if x.lstrip('-').isdigit()]

# --- MongoDB Information ---
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://goku:kZNRorqyAwj5M0fy@cluster0.plhtdqg.mongodb.net/?appName=Cluster0")
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'mn_files')

# --- File Channel Settings ---
FILE_CHANNELS = [int(ch) for ch in environ.get('FILE_CHANNELS', '-1001999941677').split()]
FILE_CHANNEL_SENDING_MODE = is_enabled(environ.get('FILE_CHANNEL_SENDING_MODE', 'False'), False)
FILE_AUTO_DELETE_SECONDS = int(environ.get('FILE_AUTO_DELETE_SECONDS', 3600))

# --- Logs & Support ---
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002793224320'))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'https://t.me/Tamilmovieslink_bot')

# --- UI & Custom Features ---
P_TTI_SHOW_OFF = is_enabled(environ.get('P_TTI_SHOW_OFF', 'False'), False)
IMDB = is_enabled(environ.get('IMDB', 'False'), False)
SINGLE_BUTTON = is_enabled(environ.get('SINGLE_BUTTON', 'True'), True)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CUSTOM_FILE_CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", "  <em>File Name</em>: <code>{file_name}</code>\n\n   <em>File Size</em>:{file_size} \n\n <b><i>Latest Movies -</i> </b>")
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", " : <a href={url}>{title}</a> \n : {year} \n : {rating}/ 10 \n : {genres}")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = is_enabled(environ.get('MELCOW_NEW_USERS', "True"), True)
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT', "False"), False)
PUBLIC_FILE_STORE = is_enabled(environ.get('PUBLIC_FILE_STORE', "False"), True)

# --- Shortlink Configurations ---
SHORTLINK_URL = environ.get("SHORTLINK_URL", "arolinks.com")
SHORTLINK_API = environ.get("SHORTLINK_API", "9142b3e52913166ef75d3b8ad05bc2e8460e9e3b")
IS_VERIFY = is_enabled(environ.get("IS_VERIFY", "True"), True)
VERIFY_EXPIRE = int(environ.get("VERIFY_EXPIRE", "600"))

# --- Search UI Stickers ---
WAIT_STICKERS = [
    "CAACAgUAAxkBAAFHdmhp4u2qHd7nMQnPWsgKNGc5nv6uogACPR0AArb0GFe5EjJNJRqswjsE",
    "CAACAgUAAxkBAAFJMAtp_2W7Dwf7shW6QWUCE9KIB9PT2wAC7h4AArhHkFe1Sv3ZskzL0zsE",
    "CAACAgUAAxkBAAFJMA1p_2W-r3AXl0xk0pyRTlLUx0y-GwACdRwAAs3b-FcQ6RRr9fdJzTsE",
    "CAACAgUAAxkBAAFJMBdp_2XtMcruOoWoi8qfxOVEwtcQrgACfSIAAkHq-VfbPPjOrj0HxTsE",
    "CAACAgUAAxkBAAFJMBlp_2XvOZBoW8id9kXVYLfHliPJlwACGR4AAvc_AAFU6k2LTq0oK147BA"
]

# --- Channel Routing Setup ---
UPDATES_CHANNEL = int(environ.get("UPDATES_CHANNEL", "-1003803095451"))
MOVIE_DB_CHANNEL = int(environ.get("MOVIE_DB_CHANNEL", "-1001999941677"))
ANIME_CHANNEL_ID = int(environ.get("ANIME_CHANNEL_ID", "-1002591922002"))
USER_REQ_DB_CHANNEL = int(environ.get("USER_REQ_DB_CHANNEL", "-1003796989516"))
ALERT_LOG_CHANNEL_ID = int(environ.get("ALERT_LOG_CHANNEL_ID", "-1003602676231"))
NEW_ALERT_LOG_CHANNEL_ID = int(environ.get("NEW_ALERT_LOG_CHANNEL_ID", ""))
MISSING_LOG_CHANNEL = int(environ.get("MISSING_LOG_CHANNEL", "-1003555146843"))
CAM_DB_CHANNEL = int(environ.get("CAM_DB_CHANNEL", "-1003952875911"))

# --- API Integrations ---
TMDB_API_KEY = environ.get("TMDB_API_KEY", "f0ed821364e340369110e83b814899ed")

# --- Log Summary Setup ---
LOG_STR = "Current Customized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"
