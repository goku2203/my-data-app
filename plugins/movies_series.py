import asyncio
import re
from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from pyrogram.types import Message
from database.ia_filterdb import get_movie_list, get_series_grouped

# --- 1 Minute Auto-Delete Helper ---
async def auto_delete_helper(msg, delay=60):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# --- Filename Cleaner Function ---
def clean_name(raw_name):
    # Username "@Goku Stark" ah thookiuduvom
    clean = re.sub(r'(?i)(?:\[|\(|@)?\s*goku[\s._-]*stark\s*(?:\]|\))?', '', raw_name)
    
    # Name and Year (eg: Drona 2008) edukka try pannuvom
    year_match = re.search(r'^(.*?)\b(19\d{2}|20\d{2})\b', clean)
    if year_match:
        title = year_match.group(1)
        year = year_match.group(2)
        title = re.sub(r'[-_./\[\]\(\)]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return f"{title.title()} ({year})"
    
    # Oruvela year illana general junk ah clean panrom (for Series)
    clean = re.sub(r'(?i)(hq|hdrip|1080p|720p|480p|x264|x265|mkv|mp4|aac|tamil|telugu|hindi|prehd|cam|scr).*', '', clean)
    clean = re.sub(r'[-_./\[\]\(\)]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean.title()

@Client.on_message(filters.private & filters.command("movies"))
async def list_movies(bot: Client, message: Message):
    movies = await get_movie_list()
    if not movies:
        k = await message.reply("😔 No recent movies found.")
        asyncio.create_task(auto_delete_helper(k, 60))
        return

    msg = "<b>🍿 Latest Uploaded Movies:</b>\n\n"
    count = 1
    added_movies = set() # Duplicates avoid panna set() use panrom

    for m in movies:
        cleaned = clean_name(m)
        # Orey movie thirumba thirumba varama thadukkum
        if cleaned and cleaned not in added_movies:
            msg += f"<b>{count}.</b> <code>{cleaned}</code> ✅\n"
            added_movies.add(cleaned)
            count += 1
        if count > 15: # 15 Movies max for neat look
            break
            
    msg += "\n<blockquote><i>⏳ This message will be auto-deleted in 1 minute.</i></blockquote>"
    k = await message.reply(msg[:4096], parse_mode=ParseMode.HTML)
    
    # User Command & Bot Message Auto Delete aagum
    asyncio.create_task(auto_delete_helper(k, 60))
    asyncio.create_task(auto_delete_helper(message, 60))

@Client.on_message(filters.private & filters.command("series"))
async def list_series(bot: Client, message: Message):
    series_data = await get_series_grouped()
    if not series_data:
        k = await message.reply("😔 No recent series found.")
        asyncio.create_task(auto_delete_helper(k, 60))
        return

    msg = "<b>📺 Latest Uploaded Series:</b>\n\n"
    count = 1

    for title, episodes in series_data.items():
        cleaned = clean_name(title)
        # Episodes list ah thookitu Name mattum display panrom
        msg += f"<b>{count}.</b> <code>{cleaned}</code> ✅\n"
        count += 1
        if count > 15:
            break
            
    msg += "\n<blockquote><i>⏳ This message will be auto-deleted in 1 minute.</i></blockquote>"
    k = await message.reply(msg[:4096], parse_mode=ParseMode.HTML)
    
    # User Command & Bot Message Auto Delete aagum
    asyncio.create_task(auto_delete_helper(k, 60))
    asyncio.create_task(auto_delete_helper(message, 60))
