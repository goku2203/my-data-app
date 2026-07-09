import re
import io
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import Media
from info import ADMINS

# Temp memory to store IDs waiting for confirmation
TEMP_DELETE_DATA = {}

def clean_movie_title(filename):
    """Clean usernames, websites, tags and unwanted filename junk."""

    # Hidden / non-breaking spaces fix
    cleaned = filename.replace("\xa0", " ")

    # Remove any Telegram username
    cleaned = re.sub(r'(?i)@goku[_\s]*stark', '', cleaned)
    cleaned = re.sub(r'@[\w_]+', '', cleaned)

    # Remove website names
    cleaned = re.sub(
        r'(?i)\b(?:www\.)?[\w-]+\.(?:com|net|org|in|me|io|co|cafe|xyz|site|link)\b',
        '',
        cleaned
    )

    # Remove starting tags: [CF], [Movies], etc.
    cleaned = re.sub(r'^\s*\[[^\]]*\]\s*', '', cleaned)

    # Remove common separators
    cleaned = cleaned.replace('_', ' ').replace('.', ' ')

    # Clean extra symbols and spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'^[\s\-_•|]+|[\s\-_•|]+$', '', cleaned)
    
    # Extract Title and Year
    match = re.search(r'(.*?)\b((?:19|20)\d{2})\b', cleaned)
    if match:
        title = match.group(1).strip()
        year = match.group(2)
        # Remove trailing hyphens or brackets
        title = re.sub(r'[\(\[\-\s]+$', '', title).strip()
        display_name = f"{title.title()} ({year})"
        unique_key = f"{title.lower()}_{year}"
        return display_name, unique_key
    else:
        # Fallback if no year is found
        title = cleaned.split('-')[0].split('[')[0].strip().title()
        return title, title.lower()

def check_quality(filename):
    """Determines if a file is an early print (CAM) or HD."""
    filename_lower = filename.lower()
    cam_keywords = ['cam', 'hdcam', 'hq cam', 'hdts', 'hdtc', 'tsrip', 'predvd', 'predvdrip', 'theater', 'theatre', 'scr', 'dvdscr', 'pdvd', 'predvbd']
    if any(kw in filename_lower for kw in cam_keywords):
        return "CAM"
    return "HD"


@Client.on_message(filters.command("cleandb") & filters.user(ADMINS))
async def clean_db(client, message):
    msg = await message.reply("⏳ **Scanning Database for PreDVD & HD prints... Please wait!**")
    
    movies_data = {}
    
    # Database scan
    cursor = Media.collection.find({})
    async for file in cursor:
        file_name = file.get("file_name", "")
        if not file_name: continue
        _id = file.get("_id")
        
        display_name, movie_key = clean_movie_title(file_name)
        quality = check_quality(file_name)
        
        if movie_key not in movies_data:
            movies_data[movie_key] = {
                "display_name": display_name,
                "predvd_ids": [],
                "hd_count": 0  # Intha idathula count add pannirukken
            }
        
        if quality == "CAM":
            movies_data[movie_key]["predvd_ids"].append(_id)
        else:
            movies_data[movie_key]["hd_count"] += 1 # HD count increase agum
            
    # Filter the scanned results
    delete_list = []
    only_predvd_list = []
    delete_ids = []
    
    for key, data in movies_data.items():
        predvd_count = len(data["predvd_ids"])
        hd_count = data["hd_count"]
        
        if predvd_count > 0: # If PreDVD exists
            # Movie name pakkathula count varra maari format
            formatted_name = f"{data['display_name']} [PreDVD: {predvd_count} | HD: {hd_count}]"
            
            if hd_count > 0:
                # Both exist -> Safe to delete PreDVD
                delete_list.append(formatted_name)
                delete_ids.extend(data["predvd_ids"])
            else:
                # Only PreDVD exists -> Keep it, needs upgrade
                only_predvd_list.append(formatted_name)
                
    if not delete_list and not only_predvd_list:
        return await msg.edit("✨ **Database is clean!** No PreDVD or CAM prints found.")

    # Text Report Building - Formatting apdiye maintain pannirukken
    report = "<blockquote>📊 <b>Database PreDVD Scan Report</b></blockquote>\n\n"
    
    if delete_list:
        report += f"<blockquote>🗑️ <b>Replaceable Early Prints (HD Available):</b></blockquote>\n"
        report += "(Safe to delete these PreDVD files)\n\n"
        for i, name in enumerate(delete_list[:30], 1): 
            report += f"{i}. `{name}`\n"
        if len(delete_list) > 30:
            report += f"... and {len(delete_list) - 30} more movies.\n"
        report += f"\n*Total PreDVD files waiting for deletion: {len(delete_ids)}*\n\n"
    else:
        report += "<blockquote>🗑️ <b>No replaceable PreDVD files found.</b></blockquote>\n\n"
        
    if only_predvd_list:
        report += f"<blockquote>⚠️ <b>Pending Upgrades (Only PreDVD Available):</b></blockquote>\n"
        report += "(Waiting for HD releases)\n\n"
        for i, name in enumerate(only_predvd_list[:30], 1):
            report += f"{i}. `{name}`\n"
        if len(only_predvd_list) > 30:
            report += f"... and {len(only_predvd_list) - 30} more movies.\n"

    # Export to .txt if the report is too long 
    full_report = "📊 DATABASE PREDVD SCAN REPORT\n=================================\n\n"
    if delete_list:
        full_report += f"🗑️ REPLACEABLE EARLY PRINTS (HD Available) - [{len(delete_ids)} Files]\n"
        full_report += "(Safe to delete these PreDVD files)\n---------------------------------\n"
        for i, name in enumerate(delete_list, 1):
            full_report += f"{i}. {name}\n"
        full_report += "\n"
    if only_predvd_list:
        full_report += f"⚠️ PENDING UPGRADES (Only PreDVD Available) - [{len(only_predvd_list)} Movies]\n"
        full_report += "(Waiting for HD releases)\n---------------------------------\n"
        for i, name in enumerate(only_predvd_list, 1):
            full_report += f"{i}. {name}\n"

    # Add Interactive Buttons
    buttons = []
    if delete_ids:
        TEMP_DELETE_DATA[message.from_user.id] = delete_ids
        buttons.append([InlineKeyboardButton("✅ Confirm & Delete PreDVDs", callback_data="confirm_delete_predvd")])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")])
    
    reply_markup = InlineKeyboardMarkup(buttons)

    # If the list is large, send the full report as a .txt file
    if len(report) > 4000 or len(delete_list) > 30 or len(only_predvd_list) > 30:
        with io.BytesIO(str.encode(full_report)) as report_file:
            report_file.name = "PreDVD_Scan_Report.txt"
            await message.reply_document(
                document=report_file,
                caption=report,
                reply_markup=reply_markup
            )
        await msg.delete()
    else:
        await msg.edit(report, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex(r"^(confirm_delete_predvd|cancel_delete)$"))
async def confirm_delete_cb(client, query):
    if query.data == "cancel_delete":
        if query.from_user.id in TEMP_DELETE_DATA:
            del TEMP_DELETE_DATA[query.from_user.id]
        
        # Entha button amukunnalum message delete aaganum
        await query.message.delete()
        return await query.answer("❌ Deletion Cancelled!", show_alert=True)
        
    if query.data == "confirm_delete_predvd":
        delete_ids = TEMP_DELETE_DATA.get(query.from_user.id)
        if not delete_ids:
            await query.message.delete()
            return await query.answer("Session expired! Please run /cleandb again.", show_alert=True)
        
        # Fast & Safe Bulk Deletion
        try:
            result = await Media.collection.delete_many({"_id": {"$in": delete_ids}})
            deleted_count = result.deleted_count
            success_text = f"**✅ Cleanup Success!**\n\nTotally **{deleted_count}** replaceable PreDVD files safely deleted from the database.\n*(Pending upgrades were kept safe)*"
            
            # DB la delete aanathum message-a delete pannitu, pudusa confirmation anuprom
            await query.message.delete()
            await client.send_message(query.message.chat.id, success_text)
            
        except Exception as e:
            await query.message.delete()
            await client.send_message(query.message.chat.id, f"**❌ Error during deletion:** `{e}`")
        finally:
            # Clear Memory
            if query.from_user.id in TEMP_DELETE_DATA:
                del TEMP_DELETE_DATA[query.from_user.id]
