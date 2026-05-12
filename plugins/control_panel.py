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

@Client.on_message(filters.command(["stats", "panel"]) & filters.user(ADMINS))
async def stats_command(client, message):
    start_t = time.time()
    tmp_msg = await message.reply_text("<b><i>⏳ Fetching Advanced System Data...</i></b>")
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
    
    # Attractive UI formatting using Quotes, Bold, and Italics
    stats_text = (
        "<blockquote><b>👑 <u>𝐎𝐖𝐍𝐄𝐑 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 𝐏𝐀𝐍𝐄𝐋</u> 👑</b></blockquote>\n\n"
        f"<i>Welcome Master {message.from_user.mention}! Here is your Bot Status.</i>\n\n"
        "<b>🤖 <u>𝐒𝐲𝐬𝐭𝐞𝐦 𝐏𝐞𝐫𝐟𝐨𝐫𝐦𝐚𝐧𝐜𝐞</u></b>\n"
        f"┣ ⏱️ <b><i>Uptime:</i></b> <code>{uptime}</code>\n"
        f"┗ 🚀 <b><i>Ping:</i></b> <code>{ping_time} ms</code>\n\n"
        "<b>📊 <u>𝐔𝐬𝐞𝐫 𝐒𝐭𝐚𝐭𝐢𝐬𝐭𝐢𝐜𝐬</u></b>\n"
        f"┣ 👤 <b><i>Total Users:</i></b> <code>{total_users}</code>\n"
        f"┣ 👥 <b><i>Total Groups:</i></b> <code>{total_chats}</code>\n"
        f"┗ 🗂️ <b><i>Total Files:</i></b> <code>{total_files}</code>\n\n"
        "<blockquote><b>💾 <u>𝐒𝐭𝐨𝐫𝐚𝐠𝐞 & 𝐃𝐚𝐭𝐚𝐛𝐚𝐬𝐞</u></b>\n"
        f"┣ 📈 <b><i>Used:</i></b> <code>{monsize_str}</code> (<code>{mongo_percent:.2f}%</code>)\n"
        f"┗ 🟢 <b><i>Free:</i></b> <code>{free}</code></blockquote>\n\n"
        "<b>🖥️ <u>𝐒𝐞𝐫𝐯𝐞𝐫 𝐇𝐚𝐫𝐝𝐰𝐚𝐫𝐞</u></b>\n"
        f"┣ ⚡ <b><i>CPU:</i></b> <code>{cpu}%</code>\n"
        f"┗ 💽 <b><i>RAM:</i></b> <code>{ram}%</code>"
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("☁️ Render Dashboard", url="https://dashboard.render.com"),
            InlineKeyboardButton("🍃 MongoDB Cloud", url="https://cloud.mongodb.com")
        ],
        [
            InlineKeyboardButton("🗑 Close Panel", callback_data="close_data")
        ]
    ])

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
