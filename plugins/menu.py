import logging
import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from Script import script
from info import PICS
from utils import temp

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex("^(start|start_data|help|about|source|manual_filter|button|auto_filter|connection)$"))
async def menu_callbacks_handler(client: Client, query: CallbackQuery):
    data = query.data
    
    if data == "start" or data == "start_data":
        buttons = [
            [
                InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{temp.U_NAME}?startgroup=true")
            ],
            [
                InlineKeyboardButton("ℹ️ Help Center", callback_data="help"),
                InlineKeyboardButton("🤖 About Bot", callback_data="about")
            ],
            [
                InlineKeyboardButton("🎭 Anime Channel", url="https://t.me/Anime_single"), 
                InlineKeyboardButton("📢 Updates Channel", url="https://t.me/super_goku_god")
            ],
            [
                InlineKeyboardButton("🧑‍💻 Contact Admin", url="https://t.me/Tamilmovieslink_bot"),
                InlineKeyboardButton("💎 Premium Plans", callback_data="premium_data")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
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
                InlineKeyboardButton("🏷 Manual Filter", callback_data="manual_filter"),
                InlineKeyboardButton("⚙️ Auto Filter", callback_data="auto_filter")
            ],
            [
                InlineKeyboardButton("🔗 Connections", callback_data="connection"),
            ],
            [
                InlineKeyboardButton("🔙 Return", callback_data="start_data"),
                InlineKeyboardButton("💎 Premium Plans", callback_data="premium_data")
            ],
            [
                InlineKeyboardButton("🧑‍💻 Contact Admin", url="https://t.me/Tamilmovieslink_bot")
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
            InlineKeyboardButton('🔙 Back', callback_data='start'),
            InlineKeyboardButton('🧑‍💻 Contact Admin', url='https://t.me/Tamilmovieslink_bot')
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
            InlineKeyboardButton('🔙 Back', callback_data='about'),
            InlineKeyboardButton('🧑‍💻 Contact Admin', url='https://t.me/Tamilmovieslink_bot')
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

    elif data == "manual_filter":
        buttons = [[
            InlineKeyboardButton('🔙 Back', callback_data='help'),
            InlineKeyboardButton('🧑‍💻 Contact Admin', url='https://t.me/Tamilmovieslink_bot'),
            InlineKeyboardButton('🔘 Button', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=random.choice(PICS),
                caption=script.MANUALFILTER_TXT,
                parse_mode=enums.ParseMode.HTML
            ),
            reply_markup=reply_markup
        )
        return await query.answer()

    elif data == "button":
        buttons = [[
            InlineKeyboardButton('🔙 Back', callback_data='help'),
            InlineKeyboardButton('🧑‍💻 Contact Admin', url='https://t.me/Tamilmovieslink_bot')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=random.choice(PICS),
                caption=script.BUTTON_TXT,
                parse_mode=enums.ParseMode.HTML
            ),
            reply_markup=reply_markup
        )
        return await query.answer()

    elif data == "auto_filter":
        buttons = [[
            InlineKeyboardButton('🔙 Back', callback_data='help'),
            InlineKeyboardButton('🧑‍💻 Contact Admin', url='https://t.me/Tamilmovieslink_bot')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=random.choice(PICS),
                caption=script.AUTOFILTER_TXT,
                parse_mode=enums.ParseMode.HTML
            ),
            reply_markup=reply_markup
        )
        return await query.answer()

    elif data == "connection":
        buttons = [[
            InlineKeyboardButton('🔙 Back', callback_data='help'),
            InlineKeyboardButton('🧑‍💻 Contact Admin', url='https://t.me/Tamilmovieslink_bot')
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
