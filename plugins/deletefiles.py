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
BATCH_SIZE = 20  # Number of files to delete in each batch
SLEEP_TIME = 2   # Seconds to wait between batches

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
        
    status_msg = await message.reply_text("🔎 Checking database... Please wait.")
    
    # Keyword regex pattern
    raw_pattern = r'(\b|[\.\+\-_])' + re.escape(keyword) + r'(\b|[\.\+\-_])'
    regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    
    # Cam/Theater words list
    cam_words = ["camrip", "hdcam", "predvd", "tsrip", "hqcam", "hcrip", "theater print", "cam", "dvdscr", "scr"]
    
    # Check Database
    cursor = Media.collection.find({'file_name': regex})
    hd_count = 0
    cam_count = 0
    
    async for doc in cursor:
        fname = doc.get("file_name", "").lower()
        # Fix: Checking caption as well (to handle truncated filename problem)
        caption = doc.get("caption", "")
        if caption is None:
            caption = ""
        caption = caption.lower()
        
        check_text = fname + " " + caption
        
        # Checking if cam words are present
        if any(x in check_text for x in cam_words):
            cam_count += 1
        else:
            hd_count += 1
            
    total_count = hd_count + cam_count
    
    if total_count == 0:
        msg = await status_msg.edit_text(f"❌ No files found for: **{keyword}**")
        asyncio.create_task(auto_delete_helper(msg, message, 30))
        return

    # Creating dynamic buttons
    buttons = []
    if hd_count > 0:
        buttons.append([InlineKeyboardButton(f"🎞 Delete HD Prints ({hd_count})", callback_data=f"deltype#hd#{keyword}")])
    if cam_count > 0:
        buttons.append([InlineKeyboardButton(f"🎥 Delete PreDVD/Cam ({cam_count})", callback_data=f"deltype#cam#{keyword}")])
    if hd_count > 0 and cam_count > 0:
        buttons.append([InlineKeyboardButton(f"🗑 Delete All ({total_count})", callback_data=f"deltype#all#{keyword}")])
        
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="close_data")])
    
    msg = await status_msg.edit_text(
        text=f"<b>Movie:</b> `{keyword}`\n<b>Total Files Found:</b> `{total_count}`\n\nPlease select which category of files you want to delete. 👇",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
    
    # Auto-deleting the menu in 30 seconds
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
    
    # Preparing query based on the selected button (Caption checking added)
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
        return await query.message.edit_text("❌ No files found to delete.", reply_markup=None)

    await query.message.edit_text(f"🗑 Deleting `{initial_count}` files... Please wait.", reply_markup=None)
    
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
# CLEANCAM CODE (SAFE VERSION WITH TEXT FILE & AUTO-DELETE)
# ==============================================================
@Client.on_message(filters.command("cleancam") & filters.user(ADMINS))
async def ask_clean_cam(client, message):
    if message.chat.type != enums.ChatType.PRIVATE:
        msg = await message.reply_text(
            "<b>Hey bro, please use this command only in my PM (Private Message)!</b>",
            parse_mode=enums.ParseMode.HTML
        )
        asyncio.create_task(auto_delete_helper(msg, message, 10))
        return
        
    status = await message.reply("🔎 Checking Database for Theater/Cam prints... Please wait.")
    
    cam_words = ["camrip", "hdcam", "predvd", "tsrip", "hqcam", "hcrip", "theater print", "cam"]
    found_files = []
    
    # Fix: Modified /cleancam to check captions as well
    cam_pattern = "|".join(cam_words)
    cam_regex = re.compile(cam_pattern, flags=re.IGNORECASE)
    
    cursor = Media.collection.find({'$or': [{'file_name': cam_regex}, {'caption': cam_regex}]})
    async for doc in cursor:
        found_files.append(doc.get("file_name", "Unknown File"))
            
    found_files = list(set(found_files))
    total_found = len(found_files)
    
    if total_found == 0:
        msg = await status.edit("✅ Database clean! No Theater/Cam prints found.")
        asyncio.create_task(auto_delete_helper(msg, message, 15))
        return
        
    file_path = "cam_prints_to_delete.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"🛑 FOUND {total_found} THEATER/CAM PRINTS:\n")
        f.write("======================================\n\n")
        for name in found_files:
            f.write(f"- {name}\n")
            
    confirm_button = InlineKeyboardButton("🗑 Yes, Delete All", callback_data="confirm_cleancam")
    abort_button = InlineKeyboardButton("❌ No, Cancel", callback_data="close_data")
    markup = InlineKeyboardMarkup([[confirm_button], [abort_button]])
    
    doc_msg = await message.reply_document(
        document=file_path,
        caption=f"⚠️ **Attention!**\n\nI searched the database and found **{total_found}** Theater/Cam prints.\n\nPlease open the `.txt` file above to check which files they are.\n\n**Do you want to permanently delete all of these?**",
        reply_markup=markup
    )
    
    await status.delete()
    if os.path.exists(file_path):
        os.remove(file_path)
        
    # Auto-deleting the cleancam message in 30 seconds
    asyncio.create_task(auto_delete_helper(doc_msg, message, 30))

@Client.on_callback_query(filters.regex(r'^confirm_cleancam$'), group=-1)
async def execute_clean_cam(client, query):
    await query.answer("Deleting Cam Prints... Please wait!", show_alert=True)
    
    try:
        await client.send_document(
            chat_id=query.from_user.id,
            document=query.message.document.file_id,
            caption="**Backup File!**\n\nHere is the list of deleted files. Please keep it safe!"
        )
    except Exception as e:
        print(f"Failed to send backup to PM: {e}")
        
    cam_words = ["camrip", "hdcam", "predvd", "tsrip", "hqcam", "hcrip", "theater print", "cam"]
    cam_pattern = "|".join(cam_words)
    cam_regex = re.compile(cam_pattern, flags=re.IGNORECASE)
    
    await Media.collection.delete_many({'$or': [{'file_name': cam_regex}, {'caption': cam_regex}]})
        
    await query.message.edit_caption(
        caption="**✅ Success!**\n\nAll Theater/Cam prints have been deleted from the database. This message will auto-delete shortly.",
        reply_markup=None 
    )
    
    await asyncio.sleep(10)
    await query.message.delete()

# ==============================================================
# AUTOMATIC PRINT ANALYZER & CAM DELETER (WITH DETAILS & COMMAND)
# ==============================================================

# 1. Manual aah pazhaya movies-a check panna pudhu command
@Client.on_message(filters.command("scanmovie") & filters.user(ADMINS))
async def manual_scan_movie(bot: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Bro, command apdiye anuppatheenga.\nUsage: `/scanmovie <movie name>`\nExample: `/scanmovie Master`")
    
    movie_name = message.text.split(" ", 1)[1]
    safe_name = movie_name[:40].strip()
    
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Analyze Prints", callback_data=f"analyze#{safe_name}")]
    ])
    await message.reply(f"**Manual Scan for:** `{movie_name}`\n\nKela irukka button-a click panni PreDVD irukka nu check pannunga.", reply_markup=btn)

# 2. Analyze button click pannumpothu nadakkura vishayam
@Client.on_callback_query(filters.regex(r'^analyze#'), group=-1)
async def analyze_movie_prints(bot: Client, query: CallbackQuery):
    movie_name = query.data.split("#")[1]
    await query.answer("Checking Database...", show_alert=False)

    raw_pattern = r'(\b|[\.\+\-_])' + re.escape(movie_name) + r'(\b|[\.\+\-_])'
    regex = re.compile(raw_pattern, flags=re.IGNORECASE)

    cam_words = ["camrip", "hdcam", "predvd", "tsrip", "hqcam", "hcrip", "theater print", "cam", "dvdscr", "scr"]
    cam_pattern = "|".join(cam_words)
    cam_regex = re.compile(cam_pattern, flags=re.IGNORECASE)

    cam_query = {
        '$and': [
            {'file_name': regex},
            {'$or': [{'file_name': cam_regex}, {'caption': cam_regex}]}
        ]
    }
    
    hd_query = {
        '$and': [
            {'file_name': regex},
            {'file_name': {'$not': cam_regex}},
            {'caption': {'$not': cam_regex}}
        ]
    }

    cam_count = await Media.count_documents(cam_query)
    hd_count = await Media.count_documents(hd_query)

    if hd_count > 0 and cam_count > 0:
        # Cam file names aah eduthu kaattura logic
        cam_files_cursor = Media.collection.find(cam_query).limit(10) # 10 files mattum kaattum
        cam_filenames = []
        async for doc in cam_files_cursor:
            cam_filenames.append(f"📄 `{doc.get('file_name', 'Unknown')}`")
        
        file_list_text = "\n".join(cam_filenames)
        
        text = f"**Movie:** `{movie_name}`\n\n✅ **HD Prints Found:** `{hd_count}`\n🎥 **PreDVD/Cam Found:** `{cam_count}`\n\n**Cam Files List:**\n{file_list_text}\n\nBoth versions exist! Intha mela irukka Cam prints aah delete pannidava?"
        
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑️ Delete PreDVD/Cam", callback_data=f"delmoviecam#{movie_name}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="close_data")]
        ])
        await query.message.reply_text(text, reply_markup=btn)
        
    elif hd_count > 0:
        await query.message.reply_text(f"**Movie:** `{movie_name}`\n\nOnly HD prints (`{hd_count}`) are available. No Cam prints found! 🎉")
        
    elif cam_count > 0:
        await query.message.reply_text(f"**Movie:** `{movie_name}`\n\nOnly PreDVD/Cam prints (`{cam_count}`) are available. We need to wait for the HD release! ⏳")
        
    else:
        await query.message.reply_text(f"Could not find files for **{movie_name}**. Spelling check pannunga.")

# 3. Delete button click pannumpothu nadakkura vishayam
@Client.on_callback_query(filters.regex(r'^delmoviecam#'), group=-1)
async def delete_specific_cam(bot: Client, query: CallbackQuery):
    movie_name = query.data.split("#")[1]
    await query.answer("Deleting Cam Prints... Please wait!", show_alert=True)

    raw_pattern = r'(\b|[\.\+\-_])' + re.escape(movie_name) + r'(\b|[\.\+\-_])'
    regex = re.compile(raw_pattern, flags=re.IGNORECASE)

    cam_words = ["camrip", "hdcam", "predvd", "tsrip", "hqcam", "hcrip", "theater print", "cam", "dvdscr", "scr"]
    cam_pattern = "|".join(cam_words)
    cam_regex = re.compile(cam_pattern, flags=re.IGNORECASE)

    cam_query = {
        '$and': [
            {'file_name': regex},
            {'$or': [{'file_name': cam_regex}, {'caption': cam_regex}]}
        ]
    }

    deleted_result = await Media.collection.delete_many(cam_query)
    
    await query.message.edit_text(f"✅ **Success!**\n\nDeleted `{deleted_result.deleted_count}` PreDVD/Cam prints for **{movie_name}**.")
    
    await asyncio.sleep(15)
    try:
        await query.message.delete()
    except:
        pass
