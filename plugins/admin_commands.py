from database.users_chats_db import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS


@Client.on_message(filters.private & filters.command("admin") & filters.user(ADMINS))
async def master_admin_panel(bot: Client, message: Message):

    admin_text = """
<b>👑 MASTER ADMIN PANEL</b>
<blockquote>Welcome back, Admin! Choose the command you need below.</blockquote>

<b>⚙️ SYSTEM & SETTINGS</b>\n
1. <code>/panel</code> — Server status & database details\n
2. <code>/settings</code> — Auto-filter settings menu\n
3. <code>/broadcast</code> — Send message to all users\n
4. <code>/restart</code> — Restart the bot safely\n
5. <code>/ping</code> — Check bot response speed\n

<b>📁 FILE MANAGEMENT</b>\n
1. <code>/deletefiles</code> or <code>/df</code>   Delete selected files from database\n
2. <code>/cleandb</code> or <code>/cd</code>   Remove all Cam / PreDVD prints\n
3. <code>/scanmovie</code> or <code>/sm</code>   Check HD and Cam files for a movie\n

<b>📡 AUTO-INDEX CHANNELS</b>\n
1. <code>/addchannel</code> — Add a new index channel\n
2. <code>/delchannel</code> — Remove an index channel\n
3. <code>/listchannels</code> — View all index channels\n

<b>🔐 FORCE SUBSCRIBE</b>\n
1. <code>/addfsub</code> — Add Force Subscribe channel\n
2. <code>/delfsub</code> — Remove Force Subscribe channel\n
3. <code>/listfsub</code> — View all Force Subscribe channels\n

<blockquote><b>💡 Tip: Command mela tap pannina easy-ah copy pannalaam.</b></blockquote>
"""

    buttons = [
        [
            InlineKeyboardButton("🏠 Home", callback_data="start_data"),
            InlineKeyboardButton("❌ Close", callback_data="close_data")
        ]
    ]

    await message.reply_text(
        text=admin_text,
        quote=True,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )

# INTHA COMPLETE UPDATED CODE-A FILE KADEISILA PODUNGA
@Client.on_message(filters.private & filters.command(["vstats", "verifystats"]) & filters.user(ADMINS))
async def verify_stats_command(bot: Client, message: Message):
    msg = await message.reply_text("⏳ **Fetching Verification Statistics... Please wait!**")
    
    daily, monthly, total, active_now = await db.get_all_verify_stats()
    
    stats_text = (
        "<blockquote><b>📊 VERIFICATION TRACKER STATS</b></blockquote>\n\n"
        f"<b>⚡ Today Verified:</b> <code>{daily}</code>\n"
        f"<b>📅 This Month Verified:</b> <code>{monthly}</code>\n"
        f"<b>🏆 All-Time Total Verified:</b> <code>{total}</code>\n\n"
        f"<b>🟢 Currently Active Users:</b> <code>{active_now}</code> <i>(10 mins limit kulla irukkavanga)</i>\n\n"
        "<i>💡 Use this data to check your Arolinks daily performance!</i>"
    )
    
    # Close button inga create pannirukkom
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Close", callback_data="close_data")]
    ])
    
    await msg.edit_text(
        stats_text, 
        parse_mode=enums.ParseMode.HTML, 
        reply_markup=buttons
    )

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Puthu /vsettings command (Admin kku mattum)
@Client.on_message(filters.private & filters.command(["vsettings"]) & filters.user(ADMINS))
async def vsettings_panel(bot: Client, message: Message):
    await send_vsettings_menu(message)

async def send_vsettings_menu(message_or_query):
    # DB la irunthu current settings ah edukkum
    v_set = await db.get_verify_settings()
    ad_set = await db.get_autodelete_settings()

    # Panel text details
    text = "<blockquote><b>  Global Bot Settings Panel</b></blockquote>\n\n"
    text += f"<b>  Verify Mode:</b> <code>{'Everytime' if v_set['mode'] == 'everytime' else 'Time Based'}</code>\n"
    if v_set['mode'] == 'time':
        text += f"<b>  Verify Time:</b> <code>{v_set['hours']} Hours</code>\n"
    
    text += f"\n<b>  Auto-Delete:</b> <code>{'Enabled' if ad_set['enabled'] else 'Disabled'}</code>\n"
    if ad_set['enabled']:
        text += f"<b>  Delete Timer:</b> <code>{ad_set['time']} Minutes</code>\n"

    # Button creations
    buttons = []
    
    # 1. Verify Option Buttons
    v_mode_text = "  Set: Time Based" if v_set['mode'] == 'everytime' else "  Set: Everytime"
    v_mode_cb = "vset_mode_time" if v_set['mode'] == 'everytime' else "vset_mode_everytime"
    buttons.append([InlineKeyboardButton(v_mode_text, callback_data=v_mode_cb)])

    # Hours change panra (+/-) buttons (Time mode la iruntha mattum varum)
    if v_set['mode'] == 'time':
        buttons.append([
            InlineKeyboardButton("  -1 Hr", callback_data="vset_hr_minus"),
            InlineKeyboardButton(f"  {v_set['hours']} Hours", callback_data="vset_hr_none"),
            InlineKeyboardButton("  +1 Hr", callback_data="vset_hr_plus")
        ])

    # 2. Auto-delete Option Buttons
    ad_mode_text = "  Enable Auto-Delete" if not ad_set['enabled'] else "  Disable Auto-Delete"
    ad_mode_cb = "adset_mode_on" if not ad_set['enabled'] else "adset_mode_off"
    buttons.append([InlineKeyboardButton(ad_mode_text, callback_data=ad_mode_cb)])

    # Minutes change panra (+/-) buttons (Auto-delete ON la iruntha mattum varum)
    if ad_set['enabled']:
        buttons.append([
            InlineKeyboardButton("  -5 Mins", callback_data="adset_min_minus"),
            InlineKeyboardButton(f"  {ad_set['time']} Mins", callback_data="adset_min_none"),
            InlineKeyboardButton("  +5 Mins", callback_data="adset_min_plus")
        ])
        
    buttons.append([InlineKeyboardButton("  Close", callback_data="close_data")])

    reply_markup = InlineKeyboardMarkup(buttons)
    
    # Message ah update pandrathu
    if isinstance(message_or_query, Message):
        await message_or_query.reply_text(text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
    else:
        await message_or_query.message.edit_text(text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)

# Button clicks ah handle panra Callback
@Client.on_callback_query(filters.regex(r"^(vset_|adset_)") & filters.user(ADMINS))
async def vsettings_callbacks(bot: Client, query: CallbackQuery):
    data = query.data
    v_set = await db.get_verify_settings()
    ad_set = await db.get_autodelete_settings()

    # Verify Logic
    if data == "vset_mode_time":
        await db.set_verify_settings("time", v_set['hours'])
    elif data == "vset_mode_everytime":
        await db.set_verify_settings("everytime", v_set['hours'])
    elif data == "vset_hr_plus":
        await db.set_verify_settings(v_set['mode'], v_set['hours'] + 1)
    elif data == "vset_hr_minus" and v_set['hours'] > 1:
        await db.set_verify_settings(v_set['mode'], v_set['hours'] - 1)
    
    # Auto-Delete Logic
    elif data == "adset_mode_on":
        await db.set_autodelete_settings(True, ad_set['time'])
    elif data == "adset_mode_off":
        await db.set_autodelete_settings(False, ad_set['time'])
    elif data == "adset_min_plus":
        await db.set_autodelete_settings(ad_set['enabled'], ad_set['time'] + 5)
    elif data == "adset_min_minus" and ad_set['time'] > 5:
        await db.set_autodelete_settings(ad_set['enabled'], ad_set['time'] - 5)
    
    elif data in ["vset_hr_none", "adset_min_none"]:
        return await query.answer("Use + or - buttons to change values!", show_alert=False)

    # Puthiya details oda menu ah refresh pandrathu
    await send_vsettings_menu(query)
    await query.answer()
