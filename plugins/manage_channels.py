import asyncio
from pyrogram import Client, filters
from info import ADMINS
from database.channel_db import add_index_channel, del_index_channel, get_all_index_channels

# --- Auto Delete Helper ---
# This will wait for 60 seconds and delete both the user command and the bot message
async def auto_delete_helper(bot_msg, user_msg, delay=60):
    await asyncio.sleep(delay)
    try:
        if bot_msg: await bot_msg.delete()
    except:
        pass
    try:
        if user_msg: await user_msg.delete()
    except:
        pass

@Client.on_message(filters.command("addchannel") & filters.user(ADMINS))
async def add_channel_cmd(client, message):
    try:
        chat_id = int(message.command[1])
        await add_index_channel(chat_id)
        await message.reply(f"✅ Success! Channel `{chat_id}` is added to the database. Auto-indexing will start now.")
    except Exception as e:
        await message.reply("❌ Invalid command. Please use this format:\n`/addchannel -100123456789`")

@Client.on_message(filters.command("delchannel") & filters.user(ADMINS))
async def del_channel_cmd(client, message):
    try:
        chat_id = int(message.command[1])
        await del_index_channel(chat_id)
        await message.reply(f"✅ Done! Channel `{chat_id}` has been removed from the database.")
    except:
        await message.reply("❌ Invalid command. Please use this format:\n`/delchannel -100123456789`")

@Client.on_message(filters.command("listchannels") & filters.user(ADMINS))
async def list_channels_cmd(client, message):
    channels = await get_all_index_channels()
    
    if not channels:
        msg = await message.reply("No channels have been added to the database yet.")
        # Auto-delete both messages after 60 seconds
        asyncio.create_task(auto_delete_helper(msg, message, 60))
        return
        
    text = "📝 **Auto-Indexing Channels List:**\n\n"
    msg = await message.reply("🔄 Fetching channel names... Please wait.")
    
    for ch in channels:
        try:
            chat = await client.get_chat(ch)
            title = chat.title
        except Exception:
            title = "Unknown Channel (Bot removed?)"
            
        text += f"🔹 **{title}**\nID: `{ch}`\n\n"
        
    await msg.edit_text(text)
    
    # Auto-delete both the bot's list message and the user's command after 60 seconds
    asyncio.create_task(auto_delete_helper(msg, message, 60))
