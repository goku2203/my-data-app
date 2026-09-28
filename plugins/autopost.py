import logging
import asyncio
import re
import aiohttp
import urllib.parse
from database.channel_db import get_all_index_channels
from pyrogram import enums
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import temp, get_size
from pyrogram.enums import ParseMode

# FIX: Inga ADMINS add pannirukken
from info import CHANNELS, UPDATES_CHANNEL, USER_REQ_DB_CHANNEL, ANIME_CHANNEL_ID, TMDB_API_KEY, ADMINS
# FIX: Inga db import add pannirukken
from database.users_chats_db import db

logger = logging.getLogger(__name__)

# --- BATCH STORAGE ---
BATCH_DATA = {}
BATCH_TASKS = {}

@Client.on_message(filters.command("autopost") & filters.user(ADMINS))
async def toggle_autopost(client, message):
    current_status = await db.get_autopost()
    state = "ON ✅" if current_status else "OFF ❌"
    
    button_text = "Turn OFF 🔴" if current_status else "Turn ON 🟢"
    callback_data = "autopost_off" if current_status else "autopost_on"
    
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(button_text, callback_data=callback_data)],
            [InlineKeyboardButton("Close ✖️", callback_data="close_data")]
        ]
    )
    
    await message.reply(
        f"**Autopost Status:** `{state}`\n\nClick the button below to change the status:",
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex(r"^autopost_(on|off)$") & filters.user(ADMINS))
async def autopost_callback(client, query: CallbackQuery):
    action = query.data.split("_")[1]
    
    if action == "on":
        await db.set_autopost(True)
        new_status = True
        msg_text = "✅ **Autopost has been ENABLED!**\nNew files will be posted to the Updates Channel."
    else:
        await db.set_autopost(False)
        new_status = False
        msg_text = "❌ **Autopost has been DISABLED!**\nNew files will NOT be posted to the Updates Channel.\n*(Files will still be saved to the database normally)*"
    
    state = "ON ✅" if new_status else "OFF ❌"
    button_text = "Turn OFF 🔴" if new_status else "Turn ON 🟢"
    callback_data = "autopost_off" if new_status else "autopost_on"
    
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(button_text, callback_data=callback_data)],
            [InlineKeyboardButton("Close ✖️", callback_data="close_data")]
        ]
    )
    
    await query.message.edit_text(
        f"{msg_text}\n\n**Current Status:** `{state}`",
        reply_markup=reply_markup
    )
    await query.answer(f"Autopost turned {action.upper()}", show_alert=False)

# --- 1. SMART INFO EXTRACTORS ---
def get_audio(filename):
    if not filename: return "Original Audio"
    filename = filename.lower()
    audio = []
    
    # Smart Detection
    if re.search(r'\b(tam|tamil)\b', filename): audio.append("Tamil")
    if re.search(r'\b(tel|telugu)\b', filename): audio.append("Telugu")
    if re.search(r'\b(hin|hindi)\b', filename): audio.append("Hindi")
    if re.search(r'\b(mal|malayalam)\b', filename): audio.append("Malayalam")
    if re.search(r'\b(kan|kannada)\b', filename): audio.append("Kannada")
    if re.search(r'\b(eng|english)\b', filename): audio.append("English")
    
    if "multi" in filename or "dual" in filename: 
        if not audio: audio.append("Multi Audio")
        
    return " - ".join(audio) if audio else "Original Audio"

def get_clean_size(size):
    size = float(size)
    if size >= 1024**3:
        return f"{size / 1024**3:.1f}GB".replace(".0", "")
    elif size >= 1024**2:
        mb = int(size / 1024**2)
        # Neenga ketta rounding logic
        if 250 <= mb <= 290:
            mb = 250
        elif 550 <= mb <= 590:
            mb = 550
        elif 720 <= mb <= 740:
            mb = 730
        elif mb > 100:
            # Matha periya MB size ellam nearest 10-kku round aagum (e.g., 412 -> 410)
            mb = int(round(mb / 10.0) * 10)
        return f"{mb}MB"
    elif size >= 1024:
        return f"{int(size / 1024)}KB"
    else:
        return f"{int(size)}B"

def get_print_quality(filename):
    if not filename: return "HD Print"
    clean = filename.lower()
    if any(x in clean for x in ["bluray", "blu-ray", "brrip", "bdrip"]):
        return "Blu-Ray"
    elif any(x in clean for x in ["web-dl", "webrip", "web", "true web-dl"]):
        return "WEB-DL"
    elif any(x in clean for x in ["hdrip", "hd-rip"]):
        return "HDRip"
    elif any(x in clean for x in ["predvd", "pre-dvd", "hqpredvd", "cam", "camrip", "hdcam"]):
        return "PreDVD (Theater Print)"
    elif any(x in clean for x in ["dvdscr", "dvd-scr"]):
        return "DVDScr"
    elif any(x in clean for x in ["1080p", "720p", "4k", "2160p"]):
        return "HD Print"
        
    return "Original Print"

def get_clean_name(name):
    if not name: return ""
    clean = name.lower()
    
    year_match = re.search(r'\b(19|20)\d{2}\b', clean)
    if year_match:
        clean = clean[:year_match.start()]
        
    clean = re.sub(r'\.(mkv|mp4|avi|flv|webm)$', '', clean)
    
    junk_list = [
        "@goku_stark", "goku stark", "trollmaa", "@skmain1", "skmain1", 
        "backup - tamil movies", "gokustark", "@gokustark", "www.", ".com", "t.me", "telegram"
    ]
    for junk in junk_list:
        clean = clean.replace(junk, "")
    clean = re.sub(r'[\[\(\{].*?[\]\)\}]', '', clean)
    clean = re.sub(r'\b\d{3,4}mb\b', '', clean)
    clean = re.sub(r'\b\d+(\.\d+)?gb\b', '', clean)
    junk_words = [
        "2160p", "4k", "1080p", "720p", "480p", "360p", 
        "hdrip", "hq", "hd", "bd", "bluray", "blu-ray", "br-rip", "brrip", "web-dl", "web",
        "dvdscr", "dvd", "cam", "hdcam", "proper", "true", "avc", "remastered", 
        "uncut", "extended", "dual", "multi", "audio", "esubs", "esub", "x264", "x265", "hevc",
        "dd5.1", "dd+", "aac", "ac3", "predvd", "pre-dvd", "hqpredvd", "hq-predvd", "camrip", 
        "print", "ddp2", "ddp", "v2", "v1", "amzn", "hotstar", "zee5", "netflix", "org", "subs"
    ]
    
    for word in junk_words:
        clean = re.sub(r'\b' + re.escape(word) + r'\b', '', clean)
    langs = ["tamil", "telugu", "hindi", "english", "tam", "tel", "hin", "eng", "malayalam", "kannada", "hqaud"]
    for lang in langs:
        clean = re.sub(r'\b' + re.escape(lang) + r'\b', '', clean)
    clean = re.sub(r'[\[\]\(\)\{\}\-_./@|:+]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    return clean.title()

def get_year(filename):
    if not filename: return "N/A"
    match = re.search(r'\b(19|20)\d{2}\b', filename)
    return match.group(0) if match else "N/A"

def get_quality_category(filename):
    if not filename: return "HD-Rip"
    filename = filename.lower()
    if "2160p" in filename or "4k" in filename: return "4K"
    if "1080p" in filename: return "FULL HD"
    if "720p" in filename: return "Only HD"
    return "HD-Rip" 

def get_quality_short(filename):
    if not filename: return "HD-Rip"
    filename = filename.lower()
    if "2160p" in filename or "4k" in filename: return "4K"
    if "1080p" in filename: return "FHD"
    if "720p" in filename: return "HD"
    return "HD-Rip"

def get_safe_name(name):
    return "\u200B".join(list(name))

async def get_tmdb_image(movie_name, year):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={urllib.parse.quote(movie_name)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                data = await response.json()
                if not data.get('results'):
                    return None
                movie = None
                if year and year != "N/A":
                    for result in data['results']:
                        res_year = result.get('release_date', '')[:4]
                        if res_year == year:
                            movie = result
                            break
                
                if not movie:
                    movie = data['results'][0]
                
                movie_id = movie['id']
                fallback_poster = f"https://image.tmdb.org/t/p/original{movie['poster_path']}" if movie.get('poster_path') else None
        images_url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={TMDB_API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(images_url) as response:
                img_data = await response.json()
                
                if img_data.get('backdrops'):
                    for backdrop in img_data['backdrops']:
                        if backdrop.get('iso_639_1') == 'ta':
                            return f"https://image.tmdb.org/t/p/original{backdrop['file_path']}"
                    
                    for backdrop in img_data['backdrops']:
                        if backdrop.get('iso_639_1') == 'en':
                            return f"https://image.tmdb.org/t/p/original{backdrop['file_path']}"
                
                return fallback_poster
    except Exception as e:
        logger.error(f"TMDB Error: {e}")
        return None

# --- 2. BATCH SENDER ---
async def send_batched_post(client, clean_name):
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        return
        
    # Adding a MASTER TRY-CATCH to catch any silent crashes
    try:
        if clean_name not in BATCH_DATA:
            return
        raw_files_list = BATCH_DATA.pop(clean_name)
        if clean_name in BATCH_TASKS:
            del BATCH_TASKS[clean_name]
        unique_files = []
        seen_sizes = set()
        for f in raw_files_list:
            if f['size'] not in seen_sizes:
                unique_files.append(f)
                seen_sizes.add(f['size'])
                
        if not unique_files:
            return
        all_audios = set()
        first_file = unique_files[0]
        
        for f in unique_files:
            langs = f['audio'].split(' - ')
            for l in langs:
                if l != "Original Audio":
                    all_audios.add(l)
        
        if all_audios:
            priority = ['Tamil', 'Telugu', 'Hindi', 'Malayalam', 'Kannada', 'English']
            sorted_audios = sorted(all_audios, key=lambda x: priority.index(x) if x in priority else 99)
            final_audio_str = " - ".join(sorted_audios)
        else:
            final_audio_str = first_file['audio']
        all_prints = set()
        for f in unique_files:
            if f['print_q']:
                all_prints.add(f['print_q'])
                
        final_print_str = " | ".join(all_prints) if all_prints else "HD Print"
        categorized = { "4K": [], "FULL HD": [], "Only HD": [], "HD-Rip": [] }
        
        for file in unique_files:
            cat = file['category']
            if cat in categorized:
                categorized[cat].append(file)
            else:
                categorized["HD-Rip"].append(file)
        safe_title = get_safe_name(clean_name)
        movie_year = first_file['year']
        
        # TMDB Image fetch
        image_url = await get_tmdb_image(clean_name, movie_year)
        # Intha edathula thaan template change pannirukken
        caption = (
            f"🎬 <b>{safe_title}</b>\n\n"
            f"<blockquote>🗓 <b><i>Year: {first_file['year']}</i></b>\n"
            f"🔊 <b><i>Audio: {final_audio_str}</i></b>\n"
            f"💿 <b><i>Quality: {final_print_str}</i></b></blockquote>\n"
            f"\u200e\n"
            f"📥 <b>Download Links:-</b>\n"
        )

        all_files_to_post = []
        order = ["HD-Rip", "Only HD", "FULL HD", "4K"]
        for category in order:
            if categorized[category]:
                all_files_to_post.extend(categorized[category])

        if not all_files_to_post:
            return

        all_files_to_post.sort(key=lambda x: x['raw_size'])

        # Files add panra logic with ├ and └
        total_files = len(all_files_to_post)
        for i, f in enumerate(all_files_to_post):
            if i == total_files - 1:
                caption += f"└ 📁 <a href='{f['link']}'><b>{f['size']}</b></a>\n"
            else:
                caption += f"├ 📁 <a href='{f['link']}'><b>{f['size']}</b></a>\n"

        caption += "━━━━━━━━━━━━━━━━━━━\n"
        caption += "<blockquote><i>(Click the file size to download)</i></blockquote>\n\n"
        caption += "<b><a href='https://t.me/howtoo1/7'>👉 How to Link Download</a></b>\n\n"
        caption += "<b><a href='https://t.me/+0TPEBg7YCZM3NDM1'>💘 Anime Single File 📂</a></b>"
        if image_url:
            await client.send_photo(
                chat_id=UPDATES_CHANNEL,
                photo=image_url,
                caption=caption,
                parse_mode=ParseMode.HTML 
            )
        else:
            await client.send_message(
                chat_id=UPDATES_CHANNEL,
                text=caption,
                parse_mode=ParseMode.HTML 
            )
        logger.info(f"✅ Post Sent: {clean_name}")
        
    except Exception as e:
        # This will catch ANY silent error and print it to the Render Logs!
        logger.error(f"❌ CRITICAL ERROR in Autopost: {e}", exc_info=True)

# --- 3. MAIN LISTENER ---
# Removed CHANNELS filter. Now it triggers dynamically based on the DB check below.
@Client.on_message((filters.document | filters.video | filters.audio), group=1)
async def media_handler(client, message):
    
    # Ignore messages sent directly to the bot (Private Chat)
    if getattr(message.chat, "type", None) == enums.ChatType.PRIVATE:
        return
        
    # Retrieve the list of allowed channels dynamically from the database
    active_channels = await get_all_index_channels()
    
    # If the message comes from an unknown channel, ignore it
    if message.chat.id not in active_channels:
        return
    try:
        media = getattr(message, message.media.value)
        file_id, file_ref = unpack_new_file_id(media.file_id)
        
        raw_name = message.caption if message.caption else media.file_name
        
        try:
            media.file_type = message.media.value
            media.caption = message.caption
            
            await save_file(media)
        except:
            pass
            
        if message.chat.id in [ANIME_CHANNEL_ID, USER_REQ_DB_CHANNEL]:
            return
        if not UPDATES_CHANNEL:
            return
        # FIX: Inga autopost on/off logic check pandrom
        is_autopost_on = await db.get_autopost()
        if not is_autopost_on:
            return  # Autopost OFF-la iruntha, db la save aagum aana channel-ku post aagathu
        clean_name = get_clean_name(raw_name)
        
        file_data = {
            'name': clean_name,
            'year': get_year(raw_name),
            'category': get_quality_category(raw_name),
            'short_q': get_quality_short(raw_name),
            'audio': get_audio(raw_name),
            'print_q': get_print_quality(raw_name), 
            'size': get_clean_size(media.file_size),
            'raw_size': media.file_size,
            'link': f"https://t.me/{temp.U_NAME}?start=filep_{file_id}"
        }
        if clean_name not in BATCH_DATA:
            BATCH_DATA[clean_name] = []
        BATCH_DATA[clean_name].append(file_data)
        if clean_name in BATCH_TASKS:
            BATCH_TASKS[clean_name].cancel()
        task = asyncio.create_task(send_batched_post(client, clean_name))
        BATCH_TASKS[clean_name] = task
        
        logger.info(f"⏳ Grouping: {clean_name} (30s Wait)")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
