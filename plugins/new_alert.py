import re
import time
import asyncio
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import MOVIE_DB_CHANNEL, USER_REQ_DB_CHANNEL, ANIME_CHANNEL_ID, ALERT_LOG_CHANNEL_ID, CAM_DB_CHANNEL
from database.ia_filterdb import Media  # Database check panna ithu thevai

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
    
    clean = re.sub(r'(?i)(?:\[|\(|@)?\s*goku[\s._-]*stark\s*(?:\]|\))?', '', clean)
    clean = re.sub(r'@\w+\s*', '', clean)
    
    match = re.search(r'(\bep?\s*\d+-\d+|\bep?\s*\d+|\b\[?e\d+|combined|cr\s|web-dl|720p|1080p|480p|x264|x265|multi audio|bluray)', clean)
    if match:
        clean = clean[:match.start()]
        
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
        
        if message.chat.id == ANIME_CHANNEL_ID:
            clean_name = get_anime_name(filename) 
        else:
            clean_name = get_movie_name(filename) 
            
        if not clean_name: clean_name = "Unknown File"
        
        # Puthusa upload aana file database la save aaga oru 2 seconds wait pandrom
        await asyncio.sleep(2)
            
        current_time = time.time()
        if clean_name in LAST_SENT:
            if current_time - LAST_SENT[clean_name] < 300: 
                return
        LAST_SENT[clean_name] = current_time

        # --- BACKGROUND AUTOMATIC DATABASE CHECK ---
        raw_pattern = r'(\b|[\.\+\-_])' + re.escape(clean_name) + r'(\b|[\.\+\-_])'
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)

        cam_words = ["camrip", "hdcam", "predvd", "tsrip", "hqcam", "hcrip", "theater print", "cam", "dvdscr", "scr"]
        cam_pattern = "|".join(cam_words)
        cam_regex = re.compile(cam_pattern, flags=re.IGNORECASE)

        cam_query = {'$and': [{'file_name': regex}, {'$or': [{'file_name': cam_regex}, {'caption': cam_regex}]}]}
        hd_query = {'$and': [{'file_name': regex}, {'file_name': {'$not': cam_regex}}, {'caption': {'$not': cam_regex}}]}

        cam_count = await Media.count_documents(cam_query)
        hd_count = await Media.count_documents(hd_query)

        safe_name = clean_name[:40].strip()
        button = None  # Default aah button illa

        # CONDITION 1: Match aagi HD & PreDVD rendu me iruntha thaan confirm delete button varum
        if hd_count > 0 and cam_count > 0:
            cam_files_cursor = Media.collection.find(cam_query).limit(10)
            cam_filenames = []
            count = 1
            async for doc in cam_files_cursor:
                cam_filenames.append(f"**{count}.** 📄 `{doc.get('file_name', 'Unknown')}`")
                count += 1
            
            file_list_text = "\n".join(cam_filenames)
            
            text = f"🚨 **Update Alert: {clean_name}** 🚨\n\nDatabase la ippo HD & PreDVD rendu me irukku!\n\n✅ **HD count:** `{hd_count}`\n🎥 **PreDVD count:** `{cam_count}`\n\n**Cam Files List:**\n{file_list_text}\n\nIntha mela irukka Cam prints aah delete pannidava?"
            
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("🗑️ Delete PreDVD/Cam", callback_data=f"delmoviecam#{safe_name}")]
            ])

        # CONDITION 2: Normal Upload (Button varaathu, verum text mattum varum)
        else:
            if message.chat.id == USER_REQ_DB_CHANNEL:
                text = f"<blockquote><b>✨ User Request Added</b></blockquote>\n\n<b>▸ {clean_name}</b>"
            elif message.chat.id == ANIME_CHANNEL_ID:
                text = f"<blockquote><b>🎬 New Anime Added</b></blockquote>\n\n<b>▸ {clean_name}</b>"
            elif message.chat.id == CAM_DB_CHANNEL:
                text = f"<blockquote><b>🎬 New Movie Added</b></blockquote>\n\n<b>▸ {clean_name}</b>"
            else:
                text = f"<b>{clean_name} Added ✅</b>"

        # MESSAGE SEND PANDRA IDAM
        if button:
            await client.send_message(
                chat_id=ALERT_LOG_CHANNEL_ID, 
                text=text, 
                parse_mode=enums.ParseMode.HTML,
                reply_markup=button
            )
        else:
            await client.send_message(
                chat_id=ALERT_LOG_CHANNEL_ID, 
                text=text, 
                parse_mode=enums.ParseMode.HTML
            )
        
    except Exception as e:
        logger.error(f"⚠️ Alert Error: {e}")
        if 'clean_name' in locals() and clean_name in LAST_SENT: 
            del LAST_SENT[clean_name]
