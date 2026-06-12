import re
import time
import logging
from pyrogram import Client, filters, enums
from info import MOVIE_DB_CHANNEL, USER_REQ_DB_CHANNEL, ANIME_CHANNEL_ID, ALERT_LOG_CHANNEL_ID, CAM_DB_CHANNEL

logger = logging.getLogger(__name__)

# Alert pora channel
LAST_SENT = {}

# 1. MOVIE NAME CLEAN FUNCTION (Normal Movies)
def get_movie_name(name):
    if not name: return "Unknown Movie"
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

# 2. ANIME NAME CLEAN FUNCTION (New Anime Selection)
def get_anime_name(name):
    if not name: return "Unknown Anime"
    clean = name.lower()
    
    # Remove tags like @Goku_Stark
    clean = re.sub(r'(?i)(?:\[|\(|@)?\s*goku[\s._-]*stark\s*(?:\]|\))?', '', clean)
    clean = re.sub(r'@\w+\s*', '', clean)
    
    # Anime file-la [E01-12], Web-DL, Quality varum pothu atha cut panna
    match = re.search(r'(\[e\d+|\be\d+|combined|cr\s|web-dl|720p|1080p|480p|x264|multi audio)', clean)
    if match:
        clean = clean[:match.start()] # Athukku appuram irukkura ellathayum remove pannidum
        
    clean = re.sub(r'\.(mkv|mp4|avi|flv|webm)$', '', clean)
    clean = re.sub(r'[\[\(\)\}\]]', '', clean)
    clean = re.sub(r'[-_./@|:+]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    return clean.title()


@Client.on_message(filters.chat([MOVIE_DB_CHANNEL, USER_REQ_DB_CHANNEL, ANIME_CHANNEL_ID, CAM_DB_CHANNEL]) & (filters.document | filters.video | filters.audio), group=10)
async def alert_handler(client, message):
    try:
        media = getattr(message, message.media.value)
        filename = message.caption if message.caption else media.file_name
        
        # --- SELECTION: ANIME VA ILLAYA NU CHECK PANDROM ---
        if message.chat.id == ANIME_CHANNEL_ID:
            clean_name = get_anime_name(filename) # Anime file cleaning
        else:
            clean_name = get_movie_name(filename) # Normal Movie cleaning
            
        if not clean_name: clean_name = "Unknown File"
            
        current_time = time.time()
        if clean_name in LAST_SENT:
            if current_time - LAST_SENT[clean_name] < 300: 
                return
        LAST_SENT[clean_name] = current_time

        # MESSAGE SEND PANDRA IDAM
        if message.chat.id == USER_REQ_DB_CHANNEL:
            text = f"<blockquote>✨ User Request Added\n\n</blockquote><b>▸ {clean_name}</b>"
        elif message.chat.id == ANIME_CHANNEL_ID:
            text = f"<blockquote>🎬 New Anime Added\n\n</blockquote><b>▸ {clean_name}</b>"
        elif message.chat.id == CAM_DB_CHANNEL:
            text = f"<blockquote>🎬 New Movie Added\n\n</blockquote><b>▸ {clean_name}</b>"
        else:
            text = f"<b>{clean_name} Added ✅</b>"

        await client.send_message(chat_id=ALERT_LOG_CHANNEL_ID, text=text, parse_mode=enums.ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"⚠️ Alert Error: {e}")
        if 'clean_name' in locals() and clean_name in LAST_SENT: 
            del LAST_SENT[clean_name]
