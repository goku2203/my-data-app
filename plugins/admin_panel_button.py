from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS 

@Client.on_message(filters.private & filters.command("admin") & filters.user(ADMINS))
async def master_admin_panel(bot: Client, message: Message):
    
    # 👑 Clean & Simple Admin List
    admin_text = """<b>👑 Master Admin Command List</b>

<i>Tap on any command below to copy it easily.</i>

<b>🛠 System & Settings</b>
<code>/panel</code> - Check server status and database info.
<code>/settings</code> - Open the auto-filter settings menu.
<code>/broadcast</code> - Reply to any message to send it to all users.
<code>/restart</code> - Safely reboot the bot system.
<code>/ping</code> - Check the bot's response speed.

<b>📂 File Management</b>
<code>/deletefiles</code> - Delete specific movie files from the DB.
<code>/cleancam</code> - Automatically find and delete all Cam/PreDVD prints.
<code>/scanmovie</code> - Check available HD and Cam prints for a movie.

<b>📡 Auto-Index Channels</b>
<code>/addchannel</code> - Add a new channel to auto-save files.
<code>/delchannel</code> - Remove an auto-index channel.
<code>/listchannels</code> - View all connected index channels.

<b>🔐 Force Subscribe (FSub)</b>
<code>/addfsub</code> - Add a new Force Subscribe channel.
<code>/delfsub</code> - Remove a Force Subscribe channel.
<code>/listfsub</code> - View all Force Subscribe channels."""

    # --- Back and Close Buttons ---
    buttons = [
        [
            InlineKeyboardButton("🔙 Back", callback_data="start_data"),
            InlineKeyboardButton("❌ Close", callback_data="close_data")
        ]
    ]

    # Fast-a reply anuppum koodave buttons-um varum
    await message.reply_text(
        text=admin_text,
        quote=True,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
