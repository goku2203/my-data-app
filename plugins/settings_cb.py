import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils import get_settings, save_group_settings
from database.connections_mdb import active_connection

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex(r"^setgs#"))
async def settings_callback_handler(client: Client, query: CallbackQuery):
    ident, set_type, status, grp_id = query.data.split("#")
    grpid = await active_connection(str(query.from_user.id))
    
    if str(grp_id) != str(grpid):
        await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
        return await query.answer()
        
    if status == "True":
        await save_group_settings(grpid, set_type, False)
    else:
        await save_group_settings(grpid, set_type, True)
        
    settings = await get_settings(grpid)
    
    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton('Filter Button', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                InlineKeyboardButton('Single' if settings["button"] else 'Double', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ Yes' if settings["botpm"] else '❌ No', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('File Secure', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Spell Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
            ],
            [
                InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_reply_markup(reply_markup)
        
    await query.answer()
