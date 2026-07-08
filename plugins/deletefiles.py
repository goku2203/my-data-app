import logging
import asyncio
import re
import os
from database.ia_filterdb import Media
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from info import ADMINS

logger = logging.getLogger(__name__)

# Constants for Batch Deletion
BATCH_SIZE = 20
SLEEP_TIME = 2

# --- 30 Seconds Auto Delete Helper ---
async def auto_delete_helper(bot_msg, user_msg, delay=30):
    await asyncio.sleep(delay)
    try:
        if bot_msg: await bot_msg.delete()
    except: pass
    try:
        if user_msg: await user_msg.delete()
    except: pass

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot: Client, message: Message):
    if message.chat.type != enums.ChatType.PRIVATE:
        msg = await message.reply_text(
            f"<b>Hey {message.from_user.mention}, this command won't work in groups. It only works in my PM!</b>",
            parse_mode=enums.ParseMode.HTML
        )
        asyncio.create_task(auto_delete_helper(msg, message, 10))
        return
    
    try:
        keyword = message.text.split(" ", 1)[1].strip()
        if not keyword:
            raise IndexError
    except IndexError:
        msg = await message.reply_text(
            f"<b>Hey {message.from_user.mention}, give me a keyword along with the command to delete files.</b>\n"
            "Usage: `/deletefiles <keyword>`\nExample: `/deletefiles master`",
            parse_mode=enums.ParseMode.HTML
        )
        asyncio.create_task(auto_delete_helper(msg, message, 15))
        return
    
    status_msg = await message.reply_text("⏳ Checking database... Please wait.")
    
    raw_pattern = r'(\b|[\.\+\-_])' + re.escape(keyword) + r'(\b|[\.\+\-_])'
    regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    cam_words = ["camrip", "hdcam", "predvd", "tsrip", "hqcam", "hcrip", "theater print", "cam", "dvdscr", "scr"]
    
    cursor = Media.collection.find({'file_name': regex})
    hd_count = 0
    cam_count = 0
    
    async for doc in cursor:
        fname = doc.get("file_name", "").lower()
        caption = doc.get("caption", "")
        if caption is None:
            caption = ""
        caption = caption.lower()
        
        check_text = fname + " " + caption
        if any(x in check_text for x in cam_words):
            cam_count += 1
        else:
            hd_count += 1
            
    total_count = hd_count + cam_count
    
    if total_count == 0:
        msg = await status_msg.edit_text(f"😔 No files found for: **{keyword}**")
        asyncio.create_task(auto_delete_helper(msg, message, 30))
        return

    buttons = []
    if hd_count > 0:
        buttons.append([InlineKeyboardButton(f"🗑 Delete HD Prints ({hd_count})", callback_data=f"deltype#hd#{keyword}")])
    if cam_count > 0:
        buttons.append([InlineKeyboardButton(f"🗑 Delete PreDVD/Cam ({cam_count})", callback_data=f"deltype#cam#{keyword}")])
    if hd_count > 0 and cam_count > 0:
        buttons.append([InlineKeyboardButton(f"🗑 Delete All ({total_count})", callback_data=f"deltype#all#{keyword}")])
    
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="close_data")])
    
    msg = await status_msg.edit_text(
        text=f"<b>Movie:</b> `{keyword}`\n<b>Total Files Found:</b> `{total_count}`\n\nPlease select which category of files you want to delete. 👇",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
    
    asyncio.create_task(auto_delete_helper(msg, message, 30))

@Client.on_callback_query(filters.regex(r'^deltype#'), group=-1)
async def confirm_and_delete_files_by_keyword(bot: Client, query: CallbackQuery):
    await query.answer("Deleting process started...", show_alert=False)
    
    _, del_type, keyword = query.data.split("#", 2)
    
    raw_pattern = r'(\b|[\.\+\-_])' + re.escape(keyword) + r'(\b|[\.\+\-_])'
    cam_words = ["camrip", "hdcam", "predvd", "tsrip", "hqcam", "hcrip", "theater print", "cam", "dvdscr", "scr"]
    cam_pattern = "|".join(cam_words)
    
    raw_regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    cam_regex = re.compile(cam_pattern, flags=re.IGNORECASE)
    
    if del_type == "all":
        filter_query = {'file_name': raw_regex}
    elif del_type == "cam":
        filter_query = {
            '$and': [
                {'file_name': raw_regex},
                {'$or': [{'file_name': cam_regex}, {'caption': cam_regex}]}
            ]
        }
    elif del_type == "hd":
        filter_query = {
            '$and': [
                {'file_name': raw_regex},
                {'file_name': {'$not': cam_regex}},
                {'caption': {'$not': cam_regex}}
            ]
        }

    initial_count = await Media.count_documents(filter_query)
    
    if initial_count == 0:
        return await query.message.edit_text("😔 No files found to delete.", reply_markup=None)

    await query.message.edit_text(f"⏳ Deleting `{initial_count}` files... Please wait.", reply_markup=None)
    
    deleted_count = 0
    while True:
        documents_to_delete = await Media.collection.find(filter_query, {"_id": 1}).limit(BATCH_SIZE).to_list(length=BATCH_SIZE)
        if not documents_to_delete:
            break
        
        ids_to_delete = [doc["_id"] for doc in documents_to_delete]
        batch_result = await Media.collection.delete_many({"_id": {"$in": ids_to_delete}})
        
        deleted_in_batch = batch_result.deleted_count
        deleted_count += deleted_in_batch
        
        await query.message.edit_text(f"⏳ Deleted `{deleted_count}` / `{initial_count}` files...")
        
        if deleted_count >= initial_count or deleted_in_batch == 0:
            break
        
        await asyncio.sleep(SLEEP_TIME)
    
    await query.message.edit_text(
        f"✅ Successfully deleted `{deleted_count}` files for keyword: **'{keyword}'**."
    )

# ==============================================================
# AUTOMATIC PRINT ANALYZER (WITH DETAILS & COMMAND)
# ==============================================================

@Client.on_message(filters.command("scanmovie") & filters.user(ADMINS))
async def direct_scan_movie(bot: Client, message: Message):
    if len(message.command) < 2:
        error_text = "<b>⚠️ Error:</b> Invalid command format!\n👉 <b>Format:</b> <code>/scanmovie <movie name></code>\n💡 <b>Example:</b> <code>/scanmovie Master</code>"
        msg = await message.reply(error_text, parse_mode=enums.ParseMode.HTML)
        asyncio.create_task(auto_delete_helper(msg, message, 15))
        return
    
    movie_name = message.text.split(" ", 1)[1]
    safe_name = movie_name[:40].strip()
    
    status_msg = await message.reply("🔍 <i>Scanning database for prints... Please wait.</i>")
    
    # Accurate Match Pattern (Matches dots, brackets, hyphens)
    raw_pattern = r'(\b|[\.\+\-_\[\]\(\)])' + re.escape(movie_name) + r'(\b|[\.\+\-_\[\]\(\)])'
    regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    
    # Updated Cam words based on your database
    cam_words = ["camrip", "hdcam", "predvd", "predvdrip", "prehd", "tsrip", "hdts", "hqcam", "hcrip", "theater print", "cam", "dvdscr", "scr"]
    cam_pattern = "|".join(cam_words)
    cam_regex = re.compile(cam_pattern, flags=re.IGNORECASE)

    # Check BOTH file_name and caption for accurate results
    movie_query = {'$or': [{'file_name': regex}, {'caption': regex}]}
    
    # Queries for Cam and HD
    cam_query = {
        '$and': [
            movie_query,
            {'$or': [{'file_name': cam_regex}, {'caption': cam_regex}]}
        ]
    }
    
    hd_query = {
        '$and': [
            movie_query,
            {'file_name': {'$not': cam_regex}},
            {'caption': {'$not': cam_regex}}
        ]
    }

    # Getting document counts
    cam_count = await Media.count_documents(cam_query)
    hd_count = await Media.count_documents(hd_query)

    # Logic 1: Both HD and Cam prints exist
    if hd_count > 0 and cam_count > 0:
        cam_files_cursor = Media.collection.find(cam_query).limit(15)
        cam_filenames = []
        count = 1
        
        async for doc in cam_files_cursor:
            raw_fname = doc.get('file_name', '')
            raw_cap = doc.get('caption', '')
            f_size = doc.get('file_size', 0)
            
            text_to_parse = str(raw_cap) if raw_cap else str(raw_fname)
            
            # 1. Clean Prefix Tags
            text_to_parse = re.sub(r'(?i)(@[\w_]+|\[CF\]|@CC\.|@WMR_|@MM_New|@DVDWOALL|@Movies_Arc)\s*[-_]*\s*', '', text_to_parse)
            
            # 2. Extract Year
            y_match = re.search(r'\b(19\d{2}|20\d{2})\b', text_to_parse)
            year = y_match.group(1) if y_match else "N/A"
            
            # 3. Extract Quality
            q_match = re.search(r'(?i)\b(1080p|720p|480p|360p|2160p|4k)\b', text_to_parse)
            quality = q_match.group(1).lower() if q_match else "N/A"
            
            # 4. Extract Size
            if f_size:
                s_mb = f_size / (1024 * 1024)
                size_str = f"{s_mb/1024:.1f}GB" if s_mb >= 1024 else f"{int(s_mb)}MB"
            else:
                s_match = re.search(r'(?i)(\d+(?:\.\d+)?\s*(?:GB|MB))', text_to_parse)
                size_str = s_match.group(1).upper().replace(' ', '') if s_match else "N/A"
            
            # 5. Extract Clean Movie Name
            c_title = text_to_parse.split(year)[0] if year != "N/A" else text_to_parse
            c_title = re.sub(r'[\(\)\[\]\.\-_]', ' ', c_title)
            c_title = re.sub(r'(?i)(tamil|telugu|hindi|malayalam|kannada|hq|predvd|cam|dvdscr|hdcam|hdrip|true|web|dl|avc|dd|aac|\bline\b|\baudio\b|remastered)', '', c_title)
            c_title = re.sub(r'\s+', ' ', c_title).strip().title()
            if len(c_title) < 2: c_title = movie_name.title()
            
            # Final Clean Display Format
            formatted_item = f"<b>{count}.</b> <code>{c_title} ({year})</code> • {quality} • {size_str}"
            cam_filenames.append(formatted_item)
            count += 1
        
        file_list_text = "\n".join(cam_filenames)
        
        text = (
            f"<b>📊 DATABASE SCAN REPORT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<b>🎬 Movie:</b> <code>{movie_name}</code>\n"
            f"<b>✅ HD Prints:</b> <code>{hd_count}</code>\n"
            f"<b>⚠️ PreDVD/Cam:</b> <code>{cam_count}</code>\n\n"
            f"<b>🗑️ CAM FILES TO DELETE:</b>\n"
            f"{file_list_text}\n\n"
            f"<i>💡 Low quality prints detected! Proceed with deletion?</i>"
        )
        
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 Wipe Cam Prints", callback_data=f"delmoviecam#{safe_name}")],
            [InlineKeyboardButton("❌ Close", callback_data="close_data")]
        ])

        await status_msg.edit_text(text, reply_markup=btn, parse_mode=enums.ParseMode.HTML)
    
    # Logic 2: Only HD prints exist
    elif hd_count > 0:
        text = (
            f"<b>📊 DATABASE SCAN REPORT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<b>🎬 Movie:</b> <code>{movie_name}</code>\n\n"
            f"<b>✅ Superb!</b> Only <b>HD prints</b> (<code>{hd_count}</code> files) exist in the database.\n"
            f"<i>No messy cam prints found!</i> ✨"
        )
        await status_msg.edit_text(text, parse_mode=enums.ParseMode.HTML)
        asyncio.create_task(auto_delete_helper(status_msg, message, 30))
    
    # Logic 3: Only Cam prints exist
    elif cam_count > 0:
        text = (
            f"<b>📊 DATABASE SCAN REPORT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<b>🎬 Movie:</b> <code>{movie_name}</code>\n\n"
            f"<b>⚠️ Warning:</b> Only <b>PreDVD/Cam</b> (<code>{cam_count}</code> files) are available right now.\n"
            f"<i>Let's wait for the HD release before deleting these.</i> ⏳"
        )
        await status_msg.edit_text(text, parse_mode=enums.ParseMode.HTML)
        asyncio.create_task(auto_delete_helper(status_msg, message, 30))
    
    # Logic 4: Movie not found
    else:
        text = (
            f"<b>📊 DATABASE SCAN REPORT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<b>❌ Error:</b> No files found for <code>{movie_name}</code>.\n"
            f"<i>Please double-check the spelling!</i> 🧐"
        )
        await status_msg.edit_text(text, parse_mode=enums.ParseMode.HTML)
        asyncio.create_task(auto_delete_helper(status_msg, message, 30))

@Client.on_callback_query(filters.regex(r'^delmoviecam#'), group=-1)
async def delete_specific_cam(bot: Client, query: CallbackQuery):
    movie_name = query.data.split("#")[1]
    await query.answer("⏳ Wiping Cam Prints... Please wait!", show_alert=True)

    raw_pattern = r'(\b|[\.\+\-_\[\]\(\)])' + re.escape(movie_name) + r'(\b|[\.\+\-_\[\]\(\)])'
    regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    
    cam_words = ["camrip", "hdcam", "predvd", "predvdrip", "prehd", "tsrip", "hdts", "hqcam", "hcrip", "theater print", "cam", "dvdscr", "scr"]
    cam_pattern = "|".join(cam_words)
    cam_regex = re.compile(cam_pattern, flags=re.IGNORECASE)

    movie_query = {'$or': [{'file_name': regex}, {'caption': regex}]}
    
    cam_query = {
        '$and': [
            movie_query,
            {'$or': [{'file_name': cam_regex}, {'caption': cam_regex}]}
        ]
    }

    deleted_result = await Media.collection.delete_many(cam_query)
    
    success_text = (
        f"<b>✅ WIPE COMPLETE</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🗑 <b>Deleted:</b> <code>{deleted_result.deleted_count}</code> Cam prints for <b>{movie_name}</b>.\n\n"
        f"<i>The database is clean now!</i> ✨"
    )
    
    await query.message.edit_text(success_text, parse_mode=enums.ParseMode.HTML)
    asyncio.create_task(auto_delete_helper(query.message, None, 15))
