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
