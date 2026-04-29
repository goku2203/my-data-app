# plugins/fsub_manager.py

import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils import is_subscribed, create_invite_links, get_missing_channels
from database.users_chats_db import db
from info import ADMINS, PICS
import random

# --- Core Function to Send the Force Sub Prompt ---
# You can easily change the photo or text here in the future
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

    # Try Again button carries the payload (like verify_xxx or file_xxx)
    bot_username = (await client.get_me()).username
    buttons.append([InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{bot_username}?start={payload}")])

    text = (
        "<b>⚠️ Access Denied!</b>\n\n"
        "<i>You must join our channels to use this bot. 👇</i>\n\n"
        "<b>🚀 How to access:</b>\n"
        "1️⃣ Join the channels below.\n"
        "2️⃣ Click the <b>'🔄 Try Again'</b> button."
    )

    # Sending with a random photo. 
    # To use a sticker later, change this to message.reply_sticker(sticker="YOUR_STICKER_ID")
    force_msg = await message.reply_photo(
        photo=random.choice(PICS), 
        caption=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
    return force_msg


# --- Commands to Manage Force Sub Channels ---

@Client.on_message(filters.command("addfsub") & filters.private)
async def add_fsub_channel(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply("🚫 Unauthorized access.")

    try:
        channel_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        return await message.reply("<b>Usage:</b> <code>/addfsub -100xxxxxxx</code>")

    channels = await db.get_auth_channels()
    if channel_id in channels:
        return await message.reply("This channel is already in the Force Sub list.")

    channels.append(channel_id)
    await db.set_auth_channels(channels)
    await message.reply(f"✅ <b>FSub Channel Added Successfully:</b>\nID: `{channel_id}`")

@Client.on_message(filters.command("delfsub") & filters.private)
async def remove_fsub_channel(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply("🚫 Unauthorized access.")

    try:
        channel_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        return await message.reply("<b>Usage:</b> <code>/delfsub -100xxxxxxx</code>")

    channels = await db.get_auth_channels()
    if channel_id not in channels:
        return await message.reply("This channel is not in the Force Sub list.")

    channels.remove(channel_id)
    await db.set_auth_channels(channels)
    await message.reply(f"🗑️ <b>FSub Channel Removed Successfully:</b>\nID: `{channel_id}`")

@Client.on_message(filters.command("listfsub") & filters.private)
async def list_fsub_channels(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply("🚫 Unauthorized access.")

    channels = await db.get_auth_channels()
    if not channels:
        return await message.reply("No Force Sub channels have been set yet.")

    text = "<b>📝 Current FSub Channels:</b>\n\n"
    for ch in channels:
        try:
            chat = await client.get_chat(ch)
            name = chat.title
        except Exception:
            name = "Unknown Channel (Check if bot is admin)"
        text += f"▪️ {name} (`{ch}`)\n"

    await message.reply(text)
