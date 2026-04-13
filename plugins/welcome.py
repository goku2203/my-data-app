import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import get_settings

# ==========================================
# EDIT PANRA AREA
# ==========================================

# 1. Sticker Setup
WELCOME_STICKER_ID = "CAACAgIAAxkBAAFGz4Vp14TkEDwLXzANxjQxctqfYSDePgAC0wUAAj-VzAqfWrvSXUfHMTsE"
LEAVE_STICKER_ID = "CAACAgIAAxkBAAFGz6Jp14akiWmHaqkF73vgliEtijxcSQACOQcAAkb7rATRJ-6r0eDcKzsE"

# 2. Welcome Messages 
WELCOME_MSG_TANGLISH = "Vanakam {mention}! Namma group-ku unnai varaverkirom. Rules-a marakkama padippa!"
WELCOME_MSG_ENGLISH = "Hello {mention}! Welcome to our group. Please make sure to read the rules!"

# 3. Leave Messages 
LEAVE_MSG_TANGLISH = "Poitu vaa {name}, unnai romba miss pannuvom nanba!"
LEAVE_MSG_ENGLISH = "Goodbye {name}, we will miss you!"

# 4. Auto Delete Timings (Seconds la)
STICKER_DELETE_TIME = 5  # Sticker 5 second la azhinjidum
MSG_DELETE_TIME = 30     # Message 30 second la azhinjidum

# ==========================================
# HELPER FUNCTION (Delete panrathukku)
# ==========================================
async def auto_delete(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# ==========================================
# MAIN SCRIPT 
# ==========================================

# Puthu user join aagumbothu
@Client.on_message(filters.new_chat_members)
async def welcome_member(client: Client, message: Message):
    # Settings check panrathu
    settings = await get_settings(message.chat.id)
    if settings and not settings.get("welcome", True):
        return 

    for member in message.new_chat_members:
        if member.id == client.me.id:
            continue # Bot aaga iruntha skip pannidum
            
        # Sticker anuppa
        sticker_msg = await message.reply_sticker(WELCOME_STICKER_ID)
        
        # Message anuppa
        welcome_text = f"{WELCOME_MSG_TANGLISH}\n\n{WELCOME_MSG_ENGLISH}".format(mention=member.mention)
        welcome_msg = await message.reply_text(text=welcome_text)
        
        # Thani thaniya delete aaga task create panrom (Unnoda style la 😉)
        asyncio.create_task(auto_delete(sticker_msg, STICKER_DELETE_TIME))
        asyncio.create_task(auto_delete(welcome_msg, MSG_DELETE_TIME))

# User group vittu pogumbothu
@Client.on_message(filters.left_chat_member)
async def leave_member(client: Client, message: Message):
    left_user = message.left_chat_member.first_name
    
    if message.left_chat_member.id == client.me.id:
        return # Bot leave aana athukku anuppathu
        
    # Sticker anuppa
    sticker_msg = await message.reply_sticker(LEAVE_STICKER_ID)
    
    # Message anuppa
    leave_text = f"{LEAVE_MSG_TANGLISH}\n\n{LEAVE_MSG_ENGLISH}".format(name=left_user)
    leave_msg = await message.reply_text(text=leave_text)
    
    # Thani thaniya delete aaga task create panrom
    asyncio.create_task(auto_delete(sticker_msg, STICKER_DELETE_TIME))
    asyncio.create_task(auto_delete(leave_msg, MSG_DELETE_TIME))
