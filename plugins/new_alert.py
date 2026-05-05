import re
import time
import logging
from pyrogram import Client, filters, enums
from info import MOVIE_DB_CHANNEL, USER_REQ_DB_CHANNEL, ANIME_CHANNEL_ID, ALERT_LOG_CHANNEL_ID

logger = logging.getLogger(__name__)

# Alert pora channel
LAST_SENT = {}

def get_name_with_year(name):
    if not name: return "Unknown File"
    clean = name.lower()
    
    clean = re.sub(r'(?i)(?:\[|\(|@)?\s*goku[\s._-]*stark\s*(?:\]|\))?', '', clean)
    clean = re.sub(r'^[\s\-_\[\]\(\)\.]+', '', clean)
    match = re.search(r'\b(19[5-9][0-9]|20[0-3][0-9])\b', clean)
    
    if match:
        end_index = match.end()
        clean = clean[:end_index]
    else:
        clean = re.sub(r'\.(mkv|mp4|avi|flv|webm)$', '', clean)
        junk_words = ["hq", "predvd", "clean", "proper", "1080p", "720p", "480p", "hdrip"]
        for word in junk_words:
            clean = re.sub(r'\b' + re.escape(word) + r'\b', '', clean)
            
    clean = re.sub(r'[\[\(\)\}\]]', '', clean)
    clean = re.sub(r'[-_./@|:+]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean.title()

@Client.on_message(filters.chat([MOVIE_DB_CHANNEL, USER_REQ_DB_CHANNEL, ANIME_CHANNEL_ID]) & (filters.document | filters.video | filters.audio), group=10)
async def alert_handler(client, message):
    try:
        media = getattr(message, message.media.value)
        filename = message.caption if message.caption else media.file_name
        clean_name = get_name_with_year(filename)
        if not clean_name: clean_name = "Unknown Movie"
            
        current_time = time.time()
        if clean_name in LAST_SENT:
            if current_time - LAST_SENT[clean_name] < 300: 
                return
        LAST_SENT[clean_name] = current_time

        # Premium Emoji HTML format. EMOJI ID ah inga mathikkalam.
        premium_emoji = '<tg-emoji emoji-id="6296367896398399651">⭐</tg-emoji>'

        # Puthu DB na User Request, Anime na Anime, illana normal
        if message.chat.id == USER_REQ_DB_CHANNEL:
            text = f"{premium_emoji} <b>{clean_name} Added ✅  [User Request]</b>"
        elif message.chat.id == ANIME_CHANNEL_ID:
            text = f"{premium_emoji} <b>{clean_name} Added ✅  [Anime]</b>"
        else:
            text = f"{premium_emoji} <b>{clean_name} Added ✅</b>"

        # Direct ah text laye premium emoji mix aagi vanthudum
        await client.send_message(chat_id=ALERT_LOG_CHANNEL_ID, text=text, parse_mode=enums.ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"⚠️ Alert Error: {e}")
        if clean_name in LAST_SENT: del LAST_SENT[clean_name]
