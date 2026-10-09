import logging
import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from Script import script
from info import PICS, ADMINS
from utils import temp

logger = logging.getLogger(__name__)

# ==========================================
# 👇 START BUTTONS INGA THAAN IRUKKANUM 👇
# ==========================================
START_BUTTONS = [
    [
        InlineKeyboardButton("➕  ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ  ➕", url=f"https://t.me/{temp.U_NAME}?startgroup=true")
    ],
    [
        InlineKeyboardButton("📚 ʜᴇʟᴘ", callback_data="help"),
        InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")
    ],
    [
        InlineKeyboardButton("🎭 ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/Anime_single"), 
        InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇꜱ", url="https://t.me/super_goku_god")
    ],
    [
        InlineKeyboardButton("🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ", url="https://t.me/Tamilmovieslink_bot"),
        InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ", callback_data="premium_data")
    ]
]

@Client.on_callback_query(filters.regex("^(start|start_data|help|about|source|connection)$"))
async def menu_callbacks_handler(client: Client, query: CallbackQuery):
    data = query.data
    
    if data == "start" or data == "start_data":
        
        # Mela irukkura START_BUTTONS ah direct ah call pandrom
        reply_markup = InlineKeyboardMarkup(START_BUTTONS)
        
        try:
            txt = script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME)
        except:
            txt = script.START_TXT.format(query.from_user.mention)
            
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=random.choice(PICS),
                caption=txt
            ),
            reply_markup=reply_markup
        )
        return await query.answer()

    elif data == "help":
        buttons = [
            [
                InlineKeyboardButton("🔍 Rᴇᴏ̨ᴜᴇsᴛ Mᴏᴠɪᴇ", url="https://t.me/Tamilmovieslink_bot")
            ],
            [
                InlineKeyboardButton("🔗 Mʏ Cᴏɴɴᴇᴄᴛɪᴏɴs", callback_data="connection"),
                InlineKeyboardButton("💎 Pʀᴇᴍɪᴜᴍ Pʟᴀɴs", callback_data="premium_data")
            ],
            [
                InlineKeyboardButton("🏠 Hᴏᴍᴇ", callback_data="start_data"),
                InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="close_data")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=random.choice(PICS),
                caption=script.HELP_TXT.format(query.from_user.mention),
                parse_mode=enums.ParseMode.HTML
            ),
            reply_markup=reply_markup
        )
        return await query.answer()

    elif data == "about":
        buttons = [[
            InlineKeyboardButton('⬅️ ʙᴀᴄᴋ', callback_data='start'),
            InlineKeyboardButton('🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ', url='https://t.me/Tamilmovieslink_bot')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=random.choice(PICS),
                caption=script.ABOUT_TXT.format(temp.B_NAME),
                parse_mode=enums.ParseMode.HTML
            ),
            reply_markup=reply_markup
        )
        return await query.answer()

    elif data == "source":
        buttons = [[
            InlineKeyboardButton('⬅️ ʙᴀᴄᴋ', callback_data='about'),
            InlineKeyboardButton('🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ', url='https://t.me/Tamilmovieslink_bot')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=random.choice(PICS),
                caption=script.SOURCE_TXT,
                parse_mode=enums.ParseMode.HTML
            ),
            reply_markup=reply_markup
        )
        return await query.answer()

    elif data == "connection":
        buttons = [[
            InlineKeyboardButton('⬅️ ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('🧑‍💻 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ', url='https://t.me/Tamilmovieslink_bot')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=random.choice(PICS),
                caption=script.CONNECTION_TXT,
                parse_mode=enums.ParseMode.HTML
            ),
            reply_markup=reply_markup
        )
        return await query.answer()
