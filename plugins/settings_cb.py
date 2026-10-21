import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils import get_settings, save_group_settings, build_settings_markup, next_auto_delete
from database.connections_mdb import active_connection
from info import ADMINS  # 👈 Inga ADMINS import add pannunga

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex(r"^setgs#"))
async def settings_callback_handler(client: Client, query: CallbackQuery):
    ident, set_type, status, grp_id = query.data.split("#")
    user_id = query.from_user.id
    
    # 🔒 ADMIN CHECK: Group Admin or Bot Admin mattum thaan change panna mudiyum
    try:
        member = await client.get_chat_member(int(grp_id), user_id)
        is_admin = member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] or user_id in ADMINS
    except Exception:
        is_admin = user_id in ADMINS

    if not is_admin:
        return await query.answer("⚠️ You are not an admin! Only admins can change these settings.", show_alert=True)
    
    # Settings change panra logic
    if status == "True":
        await save_group_settings(int(grp_id), set_type, False)
    else:
        await save_group_settings(int(grp_id), set_type, True)
        
    settings = await get_settings(int(grp_id))
    
    if settings is not None:
        await query.message.edit_reply_markup(build_settings_markup(settings, grp_id))

    await query.answer("Settings Updated! ✅")


@Client.on_callback_query(filters.regex(r"^setad#"))
async def auto_delete_cycle_handler(client: Client, query: CallbackQuery):
    """Auto Delete File button: Default -> 5 -> 10 -> 30 -> Default"""
    _, grp_id = query.data.split("#")
    user_id = query.from_user.id

    try:
        member = await client.get_chat_member(int(grp_id), user_id)
        is_admin = member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] or user_id in ADMINS
    except Exception:
        is_admin = user_id in ADMINS

    if not is_admin:
        return await query.answer("⚠️ You are not an admin! Only admins can change these settings.", show_alert=True)

    settings = await get_settings(int(grp_id))
    new_val = next_auto_delete(settings)
    await save_group_settings(int(grp_id), 'auto_delete', new_val)

    settings = await get_settings(int(grp_id))
    try:
        await query.message.edit_reply_markup(build_settings_markup(settings, grp_id))
    except Exception as e:
        logger.error(f"Auto delete markup update failed: {e}")

    msg = f"Auto Delete: {new_val} Minutes ✅" if new_val else "Auto Delete: Default ✅"
    await query.answer(msg)
