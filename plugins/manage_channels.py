from pyrogram import Client, filters
from info import ADMINS
from database.channel_db import add_index_channel, del_index_channel, get_all_index_channels

@Client.on_message(filters.command("addchannel") & filters.user(ADMINS))
async def add_channel_cmd(client, message):
    try:
        chat_id = int(message.command[1])
        await add_index_channel(chat_id)
        await message.reply(f"✅ Super bro! Channel `{chat_id}` database-la add aayiduchu. Inime automatic ah index aagum!")
    except Exception as e:
        await message.reply("⚠️ Command thappu bro. Ippadi type pannunga:\n`/addchannel -100123456789`")

@Client.on_message(filters.command("delchannel") & filters.user(ADMINS))
async def del_channel_cmd(client, message):
    try:
        chat_id = int(message.command[1])
        await del_index_channel(chat_id)
        await message.reply(f"🗑️ Done bro! Channel `{chat_id}` database-la irunthu remove aayiduchu.")
    except:
        await message.reply("⚠️ Command thappu bro. Ippadi type pannunga:\n`/delchannel -100123456789`")

@Client.on_message(filters.command("listchannels") & filters.user(ADMINS))
async def list_channels_cmd(client, message):
    channels = await get_all_index_channels()
    if not channels:
        return await message.reply("Bro, innum entha channel-um database la add pannala.")
    
    text = "📝 **Index Aagura Channels List:**\n\n"
    for ch in channels:
        text += f"🔹 `{ch}`\n"
    await message.reply(text)
