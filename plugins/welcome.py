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
WELCOME_IMAGE = "https://files.catbox.moe/48aih2.jpg"

# ==========================================

# Blockquote (>), Bold (**), Italic (__) and Emojis added

WELCOME_MSG_ENGLISH = """
> **🌟 Hello {mention}! 👋** 🎉

**✨ Welcome to our awesome group! 🎬🔥**

📜 **GROUP RULES**

🚫 No Spam / Ads
💬 Respect Everyone
📵 No 18+ Content
📢 Stay On Topic
🔁 No Reposting
👤 No Fake Info
🔒 No Personal Info

⚠️ Break rules = Mute / Ban

✨ Stay active & enjoy 💙
"""

# Inga {mention} ku badhila {name} nu maathi irukken
LEAVE_MSG_ENGLISH = """
> **👋 Goodbye {name}** 👋
We’ll miss you! 😢 Come back anytime 💙
"""

STICKER_DELETE_TIME = 4
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
            return 
            
        try:
            sticker_msg = await client.send_sticker(chat_id, WELCOME_STICKER_ID)
            asyncio.create_task(auto_delete(sticker_msg, STICKER_DELETE_TIME))
        except Exception as e:
            print(f"Welcome Sticker anuppa mudiyala: {e}")
            
        try:
            # Text-ah ready pandrom
            welcome_text = WELCOME_MSG_ENGLISH.format(mention=new.user.mention)
            
            # Photo iruntha photo-voda caption-ah text-ah anuppum, illana verum text anuppum
            if WELCOME_IMAGE:
                welcome_msg = await client.send_photo(
                    chat_id, 
                    photo=WELCOME_IMAGE, 
                    caption=welcome_text,
                    protect_content=True  # <-- Itha pudhusa add pannanum
                )
            else:
                welcome_msg = await client.send_message(
                    chat_id, 
                    text=welcome_text,
                    protect_content=True  # <-- Text ah anuppunalum forward panna mudiyathu
                )
                
            asyncio.create_task(auto_delete(welcome_msg, MSG_DELETE_TIME))
        except Exception as e:
            print(f"Welcome Text/Photo anuppa mudiyala: {e}")

    # ==========================
    # 2. User Leave Aagumbothu
    # ==========================
    elif new and new.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
        
        if new.user.id == temp.ME:
            return
            
        # Old user data illana kooda pudhusula irundhu per edukka try pannuvom
        user_name = old.user.first_name if (old and old.user) else (new.user.first_name if (new and new.user) else "Nanba")
        
        try:
            sticker_msg = await client.send_sticker(chat_id, LEAVE_STICKER_ID)
            asyncio.create_task(auto_delete(sticker_msg, STICKER_DELETE_TIME))
        except Exception:
            pass
            
        try:
            # Inga {name} nalla vela seiyum ippo
            leave_text = LEAVE_MSG_ENGLISH.format(name=user_name)
            leave_msg = await client.send_message(chat_id, text=leave_text)
            asyncio.create_task(auto_delete(leave_msg, MSG_DELETE_TIME))
        except Exception as e:
            print(f"Leave Text anuppa mudiyala: {e}")
