import logging
import asyncio
import re
import os
from database.ia_filterdb import Media
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# You MUST define ADMINS in your bot's config (e.g., info.py)
from info import ADMINS

logger = logging.getLogger(__name__)

# Constants for Batch Deletion
BATCH_SIZE = 20  # Number of files to delete in each batch
SLEEP_TIME = 2    # Seconds to wait between batches to avoid overloading the DB/bot


@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot: Client, message: Message):
    """
    Handles the /deletefiles command to prompt for confirmation before deleting
    files from the database based on a keyword in their filenames.
    This command is restricted to private chat with the bot for safety.
    """
    if message.chat.type != enums.ChatType.PRIVATE:
        return await message.reply_text(
            f"<b>Hey {message.from_user.mention}, this command won't work in groups. It only works in my PM!</b>",
            parse_mode=enums.ParseMode.HTML
        )
    
    try:
        # Extract the keyword from the command (e.g., '/deletefiles keyword')
        keyword = message.text.split(" ", 1)[1].strip()
        if not keyword:
            return await message.reply_text(
                f"<b>Hey {message.from_user.mention}, give me a keyword along with the command to delete files.</b>\n"
                "Usage: `/deletefiles <keyword>`\nExample: `/deletefiles unwanted_movie`",
                parse_mode=enums.ParseMode.HTML
            )
    except IndexError: # Catches cases where no keyword is provided after /deletefiles
        return await message.reply_text(
            f"<b>Hey {message.from_user.mention}, give me a keyword along with the command to delete files.</b>\n"
            "Usage: `/deletefiles <keyword>`\nExample: `/deletefiles unwanted_movie`",
            parse_mode=enums.ParseMode.HTML
        )
    
    # Create inline keyboard for confirmation
    confirm_button = InlineKeyboardButton("Yes, Continue !", callback_data=f"confirm_delete_files#{keyword}")
    abort_button = InlineKeyboardButton("No, Abort operation !", callback_data="close_message")
    
    markup = InlineKeyboardMarkup([[confirm_button], [abort_button]])
    
    await message.reply_text(
        text=f"<b>Are you sure? Do you want to continue deleting files with the keyword: '{keyword}'?\n\n"
             "Note: This is a destructive action and cannot be undone!</b>",
        reply_markup=markup,
        parse_mode=enums.ParseMode.HTML,
        quote=True
    )

@Client.on_callback_query(filters.regex(r'^confirm_delete_files#'))
async def confirm_and_delete_files_by_keyword(bot: Client, query: CallbackQuery):
    """
    Handles the callback query from the /deletefiles confirmation message.
    Performs batch deletion of files from the Media collection.
    """
    await query.answer() # Acknowledge the callback query

    # Extract the keyword from the callback_data
    command_prefix, keyword = query.data.split("#", 1)
    
    # Build regex to match filenames containing the keyword.
    raw_pattern = r'(\b|[\.\+\-_])' + re.escape(keyword) + r'(\b|[\.\+\-_])'
    regex = re.compile(raw_pattern, flags=re.IGNORECASE)

    # Filter query targets the 'file_name' field
    filter_query = {'file_name': regex}

    await query.message.edit_text(f"🔍 Searching for files containing **'{keyword}'** in their filenames...", parse_mode=enums.ParseMode.HTML)

    # Get the initial count of matching documents
    initial_count = await Media.count_documents(filter_query)
    if initial_count == 0:
        return await query.message.edit_text(
            f"❌ No files found with **'{keyword}'** in their filenames. Deletion aborted.",
            parse_mode=enums.ParseMode.HTML
        )

    await query.message.edit_text(
        f"Found `{initial_count}` files containing **'{keyword}'** in their filenames. Starting batch deletion...",
        parse_mode=enums.ParseMode.HTML
    )

    deleted_count = 0
    # Loop to delete in batches
    while True:
        # Fetch IDs of documents to delete in the current batch.
        documents_to_delete = await Media.collection.find(filter_query, {"_id": 1}).limit(BATCH_SIZE).to_list(length=BATCH_SIZE)
        
        if not documents_to_delete:
            break # No more documents left to delete

        # Create a list of '_id' values for the current batch
        ids_to_delete = [doc["_id"] for doc in documents_to_delete]

        # Perform the batch deletion using the collected IDs
        batch_result = await Media.collection.delete_many({"_id": {"$in": ids_to_delete}})
        
        deleted_in_batch = batch_result.deleted_count
        deleted_count += deleted_in_batch
        
        await query.message.edit_text(
            f"🗑️ Deleted `{deleted_in_batch}` files in current batch. Total deleted: `{deleted_count}` / `{initial_count}`",
            parse_mode=enums.ParseMode.HTML
        )

        if deleted_count >= initial_count or deleted_in_batch == 0:
            break # Exit loop if all found files are deleted or no more were deleted in the last batch

        await asyncio.sleep(SLEEP_TIME) # Wait before the next batch

    await query.message.edit_text(
        f"✅ Finished deletion process for keyword: **'{keyword}'**. Total files deleted: `{deleted_count}` from database.",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r'^close_message$'))
async def close_message(bot: Client, query: CallbackQuery):
    """
    Handles the 'close_message' callback to simply delete the message.
    """
    await query.answer()
    await query.message.delete()


# ==============================================================
# PUTHIYA CLEANCAM CODE (SAFE VERSION WITH TEXT FILE & AUTO-DELETE)
# ==============================================================

@Client.on_message(filters.command("cleancam") & filters.user(ADMINS))
async def ask_clean_cam(client, message):
    # Bot PM la mattum work aagura mathiri set pandrom
    if message.chat.type != enums.ChatType.PRIVATE:
        return await message.reply_text(
            "<b>Hey bro, intha command-ah Bot oda PM (Private Message) la mattum use pannunga!</b>",
            parse_mode=enums.ParseMode.HTML
        )
    
    status = await message.reply("🔍 Checking Database for Theater/Cam prints... Please wait.")
    
    cam_words = ["camrip", "hdcam", "predvd", "tsrip", "hqcam", "hcrip", "theater print", "cam"]
    found_files = []
    
    # Files ah thedi list la podurom (aana ippo delete panna maatom)
    for word in cam_words:
        cursor = Media.collection.find({"file_name": {"$regex": f"(?i){word}"}})
        async for doc in cursor:
            found_files.append(doc.get("file_name", "Unknown File"))
            
    found_files = list(set(found_files))
    total_found = len(found_files)
    
    if total_found == 0:
        return await status.edit("  Database clean! No Theater/Cam prints found.")
        
    # Text file create pandrom
    file_path = "cam_prints_to_delete.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"🎬 FOUND {total_found} THEATER/CAM PRINTS:\n")
        f.write("======================================\n\n")
        for name in found_files:
            f.write(f"- {name}\n")
            
    # Yes / No buttons create pandrom
    confirm_button = InlineKeyboardButton("✅ Yes, Delete All", callback_data="confirm_cleancam")
    abort_button = InlineKeyboardButton("❌ No, Cancel", callback_data="close_message")
    markup = InlineKeyboardMarkup([[confirm_button], [abort_button]])
    
    # Document oda serthu caption la buttons anuppurom
    await message.reply_document(
        document=file_path,
        caption=f"⚠️ **Attention!**\n\nNaan database-la thediyathula **{total_found}** Theater/Cam prints kidaichirukku.\n\nMela irukkura `.txt` file-ah open panni entha files nu check pannikonga.\n\n**Itha ellam permanent-ah delete pannanuma?**",
        reply_markup=markup
    )
    
    # Status message ah thukkidrom
    await status.delete()
    
    # System la irunthu file ah remove pandrom
    if os.path.exists(file_path):
        os.remove(file_path)

@Client.on_callback_query(filters.regex(r'^confirm_cleancam$'))
async def execute_clean_cam(client, query):
    await query.answer("Deleting Cam Prints... Please wait!", show_alert=True)[cite: 1]
    
    # --- DM ku Backup anuppura puthu code ---
    # User ku txt file ah PM la anuppa try pandrom
    try:
        await client.send_document(
            chat_id=query.from_user.id,
            document=query.message.document.file_id,
            caption="**Backup File!**\n\nHere is the list of deleted files. Please keep it safe!"
        )
    except Exception as e:
        print(f"PM ku backup anuppa mudiyala: {e}")
    # ----------------------------------------

    cam_words = ["camrip", "hdcam", "predvd", "tsrip", "hqcam", "hcrip", "theater print", "cam"][cite: 1]
    
    # Database la irunthu antha files ah delete pandrom
    for word in cam_words:[cite: 1]
        await Media.collection.delete_many({"file_name": {"$regex": f"(?i){word}"}})[cite: 1]
        
    await query.message.edit_caption(
        caption="**Success!**\n\nAll Theater/Cam prints have been deleted from the database. This message will auto-delete shortly.",
        reply_markup=None # Buttons ah remove pandrom
    )[cite: 1]
    
    # 10 seconds wait panni message ah delete pandrom
    await asyncio.sleep(10)[cite: 1]
    await query.message.delete()[cite: 1]
