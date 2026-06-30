from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.connections_mdb import add_connection, all_connections, if_active, delete_connection, make_active, make_inactive
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

# --- INGA PUTHUSA CALLBACKS ADD PANNI IRUKKEN ---
@Client.on_callback_query(filters.regex(r"^(groupcb|connectcb|disconnect|deletecb|backcb)"))
async def connection_callbacks_handler(client: Client, query: CallbackQuery):
    if "groupcb" in query.data:
        await query.answer()
        group_id = query.data.split(":")[1]
        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        
        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"
            
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("🔙 Back", callback_data="backcb")]
        ])
        
        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer()
        
    elif "connectcb" in query.data:
        await query.answer()
        group_id = query.data.split(":")[1]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id
        mkact = await make_active(str(user_id), str(group_id))
        
        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer()
        
    elif "disconnect" in query.data:
        await query.answer()
        group_id = query.data.split(":")[1]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id
        mkinact = await make_inactive(str(user_id))
        
        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer()
        
    elif "deletecb" in query.data:
        await query.answer()
        user_id = query.from_user.id
        group_id = query.data.split(":")[1]
        delcon = await delete_connection(str(user_id), str(group_id))
        
        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer()
        
    elif query.data == "backcb":
        await query.answer()
        userid = query.from_user.id
        groupids = await all_connections(str(userid))
        
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer()
            
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
                
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
