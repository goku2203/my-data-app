import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import Media
from info import ADMINS

# Regex Patterns for finding Movie Name, Year, and Quality
YEAR_REGEX = re.compile(r"(?i)(.*?)[\.\-\s\[\(]*(19\d{2}|20\d{2})")
PREDVD_REGEX = re.compile(r"(?i)(predvd|camrip|hdcam|hdtc|dvdscr|scr|pdvd|cam|predvbd)")
HD_REGEX = re.compile(r"(?i)(1080p|720p|bluray|web-dl|webrip|hdrip|hq|hd|4k)")

# Temp memory to store IDs waiting for confirmation
TEMP_DELETE_DATA = {}

@Client.on_message(filters.command("cleandb") & filters.user(ADMINS))
async def clean_db(client, message):
    msg = await message.reply("`Database scan start pandren... Konjam wait pannunga bro ⏳`")
    
    movies_data = {}
    
    # Database la irukka eppadi files-aiyum check pandrom (Memory efficient cursor)
    cursor = Media.collection.find({})
    async for file in cursor:
        file_name = file.get("file_name", "")
        _id = file.get("_id")
        
        # Name and Year extract pandrom
        match = YEAR_REGEX.search(file_name)
        if match:
            raw_name = match.group(1).replace(".", " ").replace("_", " ").strip()
            year = match.group(2)
            movie_key = f"{raw_name.lower()}_{year}" # E.g., "leo_2023"
            
            if movie_key not in movies_data:
                movies_data[movie_key] = {
                    "display_name": raw_name.title(),
                    "year": year,
                    "predvd_ids": [],
                    "hd_exists": False
                }
            
            # PreDVD ah illati HD ah nu check pandrom
            if PREDVD_REGEX.search(file_name):
                movies_data[movie_key]["predvd_ids"].append(_id)
            elif HD_REGEX.search(file_name):
                movies_data[movie_key]["hd_exists"] = True
                
    # Filter the scanned results
    delete_list = []
    only_predvd_list = []
    delete_ids = []
    
    for key, data in movies_data.items():
        if data["predvd_ids"]: # PreDVD irunthal
            if data["hd_exists"]:
                # Rendum Irukku -> List for Deletion
                delete_list.append(f"▪️ {data['display_name']} ({data['year']})")
                delete_ids.extend(data["predvd_ids"])
            else:
                # PreDVD Mattum Irukku
                only_predvd_list.append(f"▪️ {data['display_name']} ({data['year']})")
                
    # Text Report Building
    text = "**📊 Database PreDVD Scan Report**\n\n"
    
    if delete_list:
        text += f"**🗑️ HD & PreDVD Rendum Irukku (Delete Pannalam):**\n"
        for i, name in enumerate(delete_list[:30]): # First 30 movies mattum kaatum (message perusa poga koodathu)
            text += f"{i+1}. {name}\n"
        if len(delete_list) > 30:
            text += f"... and {len(delete_list) - 30} more movies.\n"
        text += f"\n*Total PreDVD files waiting for deletion: {len(delete_ids)}*\n\n"
    else:
        text += "**🗑️ Delete panna entha old PreDVD files-um illai.**\n\n"
        
    if only_predvd_list:
        text += f"**⚠️ PreDVD Mattum Irukku (HD Illai - Update Pannanum):**\n"
        for i, name in enumerate(only_predvd_list[:30]):
            text += f"{i+1}. {name}\n"
        if len(only_predvd_list) > 30:
            text += f"... and {len(only_predvd_list) - 30} more movies.\n"
            
    if not delete_list and not only_predvd_list:
        return await msg.edit("Database romba clean aah irukku bro! PreDVD files ethuvum illai. ✨")
        
    # Add Interactive Buttons
    buttons = []
    if delete_ids:
        TEMP_DELETE_DATA[message.from_user.id] = delete_ids
        buttons.append([InlineKeyboardButton("✅ Confirm & Delete PreDVDs", callback_data="confirm_delete_predvd")])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")])
    
    await msg.edit(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex(r"^(confirm_delete_predvd|cancel_delete)$"))
async def confirm_delete_cb(client, query):
    if query.data == "cancel_delete":
        if query.from_user.id in TEMP_DELETE_DATA:
            del TEMP_DELETE_DATA[query.from_user.id]
        return await query.message.edit("**❌ Deletion Cancelled! Database is untouched.**")
        
    if query.data == "confirm_delete_predvd":
        delete_ids = TEMP_DELETE_DATA.get(query.from_user.id)
        if not delete_ids:
            return await query.answer("Session expired! Please run /cleandb again.", show_alert=True)
            
        await query.message.edit("**🗑️ Deleting PreDVD files... Konjam wait pannunga...**")
        
        # Database-la irunthu bulk ah delete panrom (Fast & Safe)
        try:
            result = await Media.collection.delete_many({"_id": {"$in": delete_ids}})
            deleted_count = result.deleted_count
            await query.message.edit(f"**✅ Cleanup Success!**\n\nTotally **{deleted_count}** duplicate PreDVD files safely deleted from database.")
        except Exception as e:
            await query.message.edit(f"**❌ Error during deletion:** `{e}`")
        finally:
            # Memory clear panrom
            if query.from_user.id in TEMP_DELETE_DATA:
                del TEMP_DELETE_DATA[query.from_user.id]
