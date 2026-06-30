import asyncio
import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from utils import is_subscribed, create_invite_links, get_missing_channels, JOIN_REQUEST_USERS
from database.users_chats_db import db
from info import ADMINS, PICS

# --- Auto Delete Helper Function ---
async def auto_delete_helper(bot_msg, user_msg, delay=30):
    await asyncio.sleep(delay)
    try:
        if bot_msg: await bot_msg.delete()
    except: pass
    try:
        if user_msg: await user_msg.delete()
    except: pass

# --- Core Function to Send the Force Sub Prompt ---
async def send_fsub_prompt(client, message, payload="start"):
    missing_channels = await get_missing_channels(message.from_user.id, client)
    links = await create_invite_links(client)
    buttons = []

    if missing_channels:
        for index, channel_id in enumerate(missing_channels, start=1):
            url = links.get(channel_id)
            if url:
                buttons.append([InlineKeyboardButton(f"✨ Join Channel {index} ✨", url=url)])
    else:
        for url in links.values():
            buttons.append([InlineKeyboardButton("🤖 Join Updates Channel", url=url)])

    # 🔥 OPTIMIZATION: Faster way to get bot username without API call
    bot_username = client.me.username
    buttons.append([InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{bot_username}?start={payload}")])

    text = (
        "<b>⚠️ Access Denied!</b>\n\n"
        "<i>You must join our channels to use this bot. 👇</i>\n\n"
        "<b>🚀 How to access:</b>\n"
        "1️⃣ Join the channels below.\n"
        "2️⃣ Click the <b>'🔄 Try Again'</b> button."
    )

    # Note: ibb.co direct image link aaga irunthaal innum fast aaga work aagum (e.g., https://i.ibb.co/...)
    TELEGRAM_IMG_ID = "https://ibb.co/GvGqcxdH" 

    try:
        # 🔥 FIX: Animation kku bathila reply_photo use panniyachu
        force_msg = await message.reply_photo(
            photo=TELEGRAM_IMG_ID, 
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        # Oruvela link work aagalana, automatic ah random pic eduthukkum! (Safe mode)
        print(f"Force Sub Image Error: {e}")
        force_msg = await message.reply_photo(
            photo=random.choice(PICS), 
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    
    # 60 seconds-la auto delete
    asyncio.create_task(auto_delete_helper(force_msg, message, 60))
    
    return force_msg


# --- Commands to Manage Force Sub Channels ---

@Client.on_message(filters.command("addfsub") & filters.private)
async def add_fsub_channel(client, message):
    if message.from_user.id not in ADMINS:
        k = await message.reply("🚫 Unauthorized access.")
        asyncio.create_task(auto_delete_helper(k, message, 10))
        return

    try:
        channel_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        k = await message.reply("<b>Usage:</b> <code>/addfsub -100xxxxxxx</code>")
        asyncio.create_task(auto_delete_helper(k, message, 15))
        return

    channels = await db.get_auth_channels()
    if channel_id in channels:
        k = await message.reply("This channel is already in the Force Sub list.")
        asyncio.create_task(auto_delete_helper(k, message, 15))
        return

    channels.append(channel_id)
    await db.set_auth_channels(channels)
    k = await message.reply(f"✅ <b>FSub Channel Added Successfully:</b>\nID: `{channel_id}`")
    asyncio.create_task(auto_delete_helper(k, message, 30))

@Client.on_message(filters.command("delfsub") & filters.private)
async def remove_fsub_channel(client, message):
    if message.from_user.id not in ADMINS:
        k = await message.reply("🚫 Unauthorized access.")
        asyncio.create_task(auto_delete_helper(k, message, 10))
        return

    try:
        channel_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        k = await message.reply("<b>Usage:</b> <code>/delfsub -100xxxxxxx</code>")
        asyncio.create_task(auto_delete_helper(k, message, 15))
        return

    channels = await db.get_auth_channels()
    if channel_id not in channels:
        k = await message.reply("This channel is not in the Force Sub list.")
        asyncio.create_task(auto_delete_helper(k, message, 15))
        return

    channels.remove(channel_id)
    await db.set_auth_channels(channels)
    k = await message.reply(f"🗑️ <b>FSub Channel Removed Successfully:</b>\nID: `{channel_id}`")
    asyncio.create_task(auto_delete_helper(k, message, 30))

@Client.on_message(filters.command("listfsub") & filters.private)
async def list_fsub_channels(client, message):
    if message.from_user.id not in ADMINS:
        k = await message.reply("🚫 Unauthorized access.")
        asyncio.create_task(auto_delete_helper(k, message, 10))
        return

    channels = await db.get_auth_channels()
    if not channels:
        k = await message.reply("No Force Sub channels have been set yet.")
        asyncio.create_task(auto_delete_helper(k, message, 15))
        return

    text = "<b>📝 Current FSub Channels:</b>\n\n"
    for ch in channels:
        try:
            chat = await client.get_chat(ch)
            name = chat.title
        except Exception:
            name = "Unknown Channel (Check if bot is admin)"
        text += f"▪️ {name} (`{ch}`)\n"

    k = await message.reply(text)
    asyncio.create_task(auto_delete_helper(k, message, 60))

@Client.on_message(filters.command("clear_join_users") & filters.user(ADMINS))
async def clear_join_users(_, message: Message):
    JOIN_REQUEST_USERS.clear()
    await message.reply_text("✅ Cleared all join request users.")
