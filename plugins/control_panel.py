import time
import psutil
import asyncio
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from database.ia_filterdb import Media
from info import ADMINS, BOT_START_TIME, PICS
import random
from utils import get_size

# Refresh-kum, command-kum common-a data edukka intha function
async def get_panel_data(user_mention):
    start_t = time.time()
    ping_time = round((time.time() - start_t) * 1000, 2)
    
    uptime_sec = int(time.time() - BOT_START_TIME)
    uptime = f"{uptime_sec // 86400}d {(uptime_sec % 86400) // 3600}h {(uptime_sec % 3600) // 60}m"
    
    total_users = await db.total_users_count()
    total_chats = await db.total_chat_count()
    total_files = await Media.collection.count_documents({})
    
    monsize = await db.get_db_size()
    db_size_mb = monsize / (1024 * 1024)
    mongo_percent = (db_size_mb / 512) * 100
    free = get_size(536870912 - monsize)
    monsize_str = get_size(monsize)
    
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    
    # Neenga update panna same attractive UI
    stats_text = (
        "<blockquote><b>👑 𝗢𝗪𝗡𝗘𝗥 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 𝗣𝗔𝗡𝗘𝗟 👑</b></blockquote>\n\n"
        f"<i>Welcome Master {user_mention}! Here is your Bot Status.</i>\n\n"
        "<b>🤖 <u>𝗦𝘆𝘀𝘁𝗲𝗺 𝗣𝗲𝗿𝗳𝗼𝗿𝗺𝗮𝗻𝗰𝗲</u></b>\n"
        f"┣ ⏱️ <b>Uptime:</b> <code>{uptime}</code>\n"
        f"┗ 🚀 <b>Ping:</b> <code>{ping_time} ms</code>\n\n"
        "<b>📊 <u>𝗨𝘀𝗲𝗿 𝗦𝘁𝗮𝘁𝗶𝘀𝘁𝗶𝗰𝘀</u></b>\n"
        f"┣ 👤 <b>Total Users:</b> <code>{total_users}</code>\n"
        f"┣ 👥 <b>Total Groups:</b> <code>{total_chats}</code>\n"
        f"┗ 🗂️ <b>Total Files:</b> <code>{total_files}</code>\n\n"
        "<b>💾 <u>𝗦𝘁𝗼𝗿𝗮𝗴𝗲 & 𝗗𝗮𝘁𝗮𝗯𝗮𝘀𝗲 (𝗠𝗼𝗻𝗴𝗼𝗗𝗕)</u></b>\n"
        f"┣ 📈 <b>Used:</b> <code>{monsize_str}</code> (<code>{mongo_percent:.2f}%</code>)\n"
        f"┗ 🟢 <b>Free:</b> <code>{free}</code>\n\n"
        "<b>🖥️ <u>𝗦𝗲𝗿𝘃𝗲𝗿 𝗛𝗮𝗿𝗱𝘄𝗮𝗿𝗲 (𝗥𝗲𝗻𝗱𝗲𝗿 𝗖𝗹𝗼𝘂𝗱)</u></b>\n"
        f"┣ ⚡ <b>CPU:</b> <code>{cpu}%</code>\n"
        f"┗ 💽 <b>RAM:</b> <code>{ram}%</code>"
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("☁️ Render Dashboard", url="https://dashboard.render.com"),
            InlineKeyboardButton("🍃 MongoDB Cloud", url="https://cloud.mongodb.com")
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_panel"),
            InlineKeyboardButton("🗑 Close Panel", callback_data="close_data")
        ]
    ])
    
    return stats_text, buttons

@Client.on_message(filters.command(["stats", "panel"]) & filters.user(ADMINS))
async def stats_command(client, message):
    tmp_msg = await message.reply_text("<b><i>⏳ Fetching Advanced System Data...</i></b>")
    
    stats_text, buttons = await get_panel_data(message.from_user.mention)
    
    await tmp_msg.delete()
    
    try:
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=stats_text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(
            text=stats_text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

# Refresh button-kanda Callback Handler
@Client.on_callback_query(filters.regex("^refresh_panel$") & filters.user(ADMINS))
async def refresh_panel_callback(client, callback_query):
    try:
        await callback_query.answer("🔄 Refreshing Control Panel...", show_alert=False)
        
        # Puthu updated data edukkurom
        stats_text, buttons = await get_panel_data(callback_query.from_user.mention)
        
        # Message photo va iruntha caption ah mathanum
        if callback_query.message.photo:
            await callback_query.message.edit_caption(
                caption=stats_text,
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            # Text ah iruntha athai mathanum
            await callback_query.message.edit_text(
                text=stats_text,
                reply_markup=buttons,
                parse_mode=enums.ParseMode.HTML
            )
    except Exception as e:
        # Same data va iruntha MessageNotModified error varum, atha thadukka intha except block
        pass
