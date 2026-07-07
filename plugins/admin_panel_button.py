from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS


@Client.on_message(filters.private & filters.command("admin") & filters.user(ADMINS))
async def master_admin_panel(bot: Client, message: Message):

    admin_text = """
<b>👑 MASTER ADMIN PANEL</b>
<blockquote>Welcome back, Admin! Choose the command you need below.</blockquote>

<b>⚙️ SYSTEM & SETTINGS</b>
[<code>/panel</code>] — Server status & database details\n
[<code>/settings</code>] — Auto-filter settings menu\n
[<code>/broadcast</code>] — Send message to all users\n
[<code>/restart</code>] — Restart the bot safely\n
[<code>/ping</code>] — Check bot response speed\n

<b>📁 FILE MANAGEMENT</b>
[<code>/deletefiles</code>] — Delete selected files from database\n
[<code>/cleancam</code>] — Remove all Cam / PreDVD prints\n
[<code>/scanmovie</code>] — Check HD and Cam files for a movie\n

<b>📡 AUTO-INDEX CHANNELS</b>
[<code>/addchannel</code>] — Add a new index channel\n
[<code>/delchannel</code>] — Remove an index channel\n
[<code>/listchannels</code>] — View all index channels\n

<b>🔐 FORCE SUBSCRIBE</b>
[<code>/addfsub</code>] — Add Force Subscribe channel\n
[<code>/delfsub</code>] — Remove Force Subscribe channel\n
[<code>/listfsub</code>] — View all Force Subscribe channels\n

<blockquote>💡 Tip: Command mela tap pannina easy-ah copy pannalaam.</blockquote>
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
