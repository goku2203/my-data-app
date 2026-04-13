import asyncio
from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
from utils import get_settings, temp

# ==========================================
# EDIT PANRA AREA
# ==========================================

WELCOME_STICKER_ID = "CAACAgIAAxkBAAFGz4Vp14TkEDwLXzANxjQxctqfYSDePgAC0wUAAj-VzAqfWrvSXUfHMTsE"
LEAVE_STICKER_ID = "CAACAgIAAxkBAAFGz6Jp14akiWmHaqkF73vgliEtijxcSQACOQcAAkb7rATRJ-6r0eDcKzsE"

WELCOME_MSG_TANGLISH = "Vanakam {mention}! Namma group-ku unnai varaverkirom. Rules-a marakkama padippa!"
WELCOME_MSG_ENGLISH = "Hello {mention}! Welcome to our group. Please make sure to read the rules!"

LEAVE_MSG_TANGLISH = "Poitu vaa {name}, unnai romba miss pannuvom nanba!"
LEAVE_MSG_ENGLISH = "Goodbye {name}, we will miss you!"

STICKER_DELETE_TIME = 5
MSG_DELETE_TIME = 30

async def auto_delete(msg, delay):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# ==========================================
# MAIN SCRIPT (Chat Member Updated)
# ==========================================

@Client.on_chat_member_updated(filters.group, group=10)
async def welcome_leave_handler(client: Client, update: ChatMemberUpdated):
    chat_id = update.chat.id
    settings = await get_settings(chat_id)
    
    # Settings off aagi iruntha vela seiyathu
    if settings and not settings.get("welcome", True):
        return
        
    old = update.old_chat_member
    new = update.new_chat_member
    
    # ==========================
    # 1. Puthu User Join Aagumbothu
    # ==========================
    if new and new.status == ChatMemberStatus.MEMBER and (not old or old.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED]):
        
        if new.user.id == temp.ME:
            return # Bot-kku anuppa koodathu
            
        try:
            sticker_msg = await client.send_sticker(chat_id, WELCOME_STICKER_ID)
            asyncio.create_task(auto_delete(sticker_msg, STICKER_DELETE_TIME))
        except Exception as e:
            print(f"Welcome Sticker anuppa mudiyala: {e}")
            
        try:
            welcome_text = f"{WELCOME_MSG_TANGLISH}\n\n{WELCOME_MSG_ENGLISH}".format(mention=new.user.mention)
            welcome_msg = await client.send_message(chat_id, text=welcome_text)
            asyncio.create_task(auto_delete(welcome_msg, MSG_DELETE_TIME))
        except Exception as e:
            print(f"Welcome Text anuppa mudiyala: {e}")

    # ==========================
    # 2. User Leave Aagumbothu
    # ==========================
    elif new and new.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED] and old and old.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        
        if new.user.id == temp.ME:
            return
            
        user_name = old.user.first_name if old.user else "Nanba"
        
        try:
            sticker_msg = await client.send_sticker(chat_id, LEAVE_STICKER_ID)
            asyncio.create_task(auto_delete(sticker_msg, STICKER_DELETE_TIME))
        except Exception:
            pass
            
        try:
            leave_text = f"{LEAVE_MSG_TANGLISH}\n\n{LEAVE_MSG_ENGLISH}".format(name=user_name)
            leave_msg = await client.send_message(chat_id, text=leave_text)
            asyncio.create_task(auto_delete(leave_msg, MSG_DELETE_TIME))
        except Exception:
            pass
