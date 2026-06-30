from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.connections_mdb import add_connection, all_connections, if_active, delete_connection
from info import ADMINS
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Helper function to get User ID (Handles Anonymous Admin)
def get_user_id(message):
    if message.from_user:
        return message.from_user.id
    elif message.sender_chat:
        return message.sender_chat.id
    return None

@Client.on_message((filters.private | filters.group) & filters.command('connect'))
async def addconnection(client, message):
    userid = get_user_id(message)
    if not userid:
        return await message.reply("You are anonymous, use /connect chatid in PM")
    
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        try:
            _, group_id = message.text.split(" ", 1)
        except:
            return await message.reply("Format: /connect groupid", quote=True)
    else:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and userid not in ADMINS:
            return await message.reply("You must be an admin!", quote=True)
    except:
        return await message.reply("Invalid Group ID or Bot not in group!", quote=True)

    ttl = await client.get_chat(group_id)
    addcon = await add_connection(str(group_id), str(userid))
    
    if addcon:
        await message.reply(f"Connected to **{ttl.title}**!", quote=True)
        if chat_type != enums.ChatType.PRIVATE:
            await client.send_message(userid, f"Connected to **{ttl.title}**!")
    else:
        await message.reply("Already connected!", quote=True)

@Client.on_message((filters.private | filters.group) & filters.command('disconnect'))
async def deleteconnection(client, message):
    userid = get_user_id(message)
    if not userid: return
    
    group_id = message.chat.id if message.chat.type != enums.ChatType.PRIVATE else None
    if not group_id:
        return await message.reply("Run /connections to manage groups!")

    delcon = await delete_connection(str(userid), str(group_id))
    if delcon:
        await message.reply("Successfully disconnected", quote=True)
    else:
        await message.reply("Not connected to this chat!", quote=True)

@Client.on_message(filters.private & filters.command(["connections"]))
async def connections(client, message):
    userid = message.from_user.id
    groupids = await all_connections(str(userid))
    
    if not groupids:
        return await message.reply("No active connections!", quote=True)

    buttons = []
    for groupid in groupids:
        try:
            ttl = await client.get_chat(int(groupid))
            active = await if_active(str(userid), str(groupid))
            act = " - ACTIVE" if active else ""
            buttons.append([InlineKeyboardButton(f"{ttl.title}{act}", callback_data=f"groupcb:{groupid}")])
        except: continue
        
    await message.reply("Your connected groups:", reply_markup=InlineKeyboardMarkup(buttons), quote=True)
