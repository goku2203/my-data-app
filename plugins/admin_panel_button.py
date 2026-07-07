from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from info import ADMINS 

# Menu-va uruvakkura function (Back button click pannumbothu ithu thevaipadum)
def get_admin_menu():
    panel_text = (
        "<b>👑 Admin Control Panel</b>\n\n"
        "<i>Welcome! Here is your complete set of admin tools. "
        "Select any option below to view its usage guide.</i>"
    )
    buttons = [
        [
            InlineKeyboardButton("📊 Bot Stats", callback_data="admin_panel"),
            InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton("♻️ Restart Bot", callback_data="admin_restart")
        ],
        [
            InlineKeyboardButton("🗑 Delete Files", callback_data="admin_deletefiles"),
            InlineKeyboardButton("🧹 Clean Cam/PreDVD", callback_data="admin_cleancam")
        ],
        [
            InlineKeyboardButton("🔎 Scan Movie", callback_data="admin_scanmovie"),
            InlineKeyboardButton("🏓 Ping", callback_data="admin_ping")
        ],
        [
            InlineKeyboardButton("➕ Add Channel", callback_data="admin_addchannel"),
            InlineKeyboardButton("➖ Del Channel", callback_data="admin_delchannel")
        ],
        [
            InlineKeyboardButton("📋 List All Channels", callback_data="admin_listchannels")
        ],
        [
            InlineKeyboardButton("➕ Add FSub", callback_data="admin_addfsub"),
            InlineKeyboardButton("➖ Del FSub", callback_data="admin_delfsub")
        ],
        [
            InlineKeyboardButton("📋 List All FSub", callback_data="admin_listfsub")
        ],
        [
            InlineKeyboardButton("❌ Close Panel", callback_data="close_data")
        ]
    ]
    return panel_text, InlineKeyboardMarkup(buttons)

# 1. Command-a type pannum pothu menu varum
@Client.on_message(filters.private & filters.command("admin") & filters.user(ADMINS))
async def master_admin_panel(bot: Client, message: Message):
    text, markup = get_admin_menu()
    await message.reply_text(text=text, reply_markup=markup, quote=True, parse_mode=enums.ParseMode.HTML)

# 2. Button-a click pannum pothu intha reaction nadakkum
@Client.on_callback_query(filters.regex(r"^admin_") & filters.user(ADMINS))
async def admin_button_actions(client: Client, query: CallbackQuery):
    data = query.data
    await query.answer() # Ithu thaan button mela suthura loading-a udane nippattum!
    
    # Back button click panna thirumba main menu varum
    if data == "admin_home":
        text, markup = get_admin_menu()
        await query.message.edit_text(text=text, reply_markup=markup, parse_mode=enums.ParseMode.HTML)
        return

    # Ovvoru button-kkum enna text varanum nu inga theliva irukku
    guides = {
        "admin_panel": "<b>📊 Bot Stats:</b>\n\nType <code>/panel</code> or <code>/stats</code> to view the advanced server status and database size.",
        "admin_settings": "<b>⚙️ Settings:</b>\n\nType <code>/settings</code> in your PM or inside a group to manage auto-filter settings.",
        "admin_broadcast": "<b>📢 Broadcast:</b>\n\nReply to any message/photo/video with the command <code>/broadcast</code> to send it to all users.",
        "admin_restart": "<b>♻️ Restart Bot:</b>\n\nType <code>/restart</code> to safely reboot the bot system.",
        "admin_deletefiles": "<b>🗑 Delete Files:</b>\n\nType <code>/deletefiles movie name</code> to delete specific files from the database.",
        "admin_cleancam": "<b>🧹 Clean Cam Prints:</b>\n\nType <code>/cleancam</code> to automatically find and delete all PreDVD/Cam prints.",
        "admin_scanmovie": "<b>🔎 Scan Movie:</b>\n\nType <code>/scanmovie movie name</code> to check how many HD and Cam prints are available for a specific movie.",
        "admin_ping": "<b>🏓 Ping:</b>\n\nType <code>/ping</code> to check the bot's response time.",
        "admin_addchannel": "<b>➕ Add Channel:</b>\n\nType <code>/addchannel -100xxxxxx</code> to add a new channel for auto-indexing.",
        "admin_delchannel": "<b>➖ Del Channel:</b>\n\nType <code>/delchannel -100xxxxxx</code> to remove a channel from auto-indexing.",
        "admin_listchannels": "<b>📋 List Channels:</b>\n\nType <code>/listchannels</code> to see all connected auto-index channels.",
        "admin_addfsub": "<b>➕ Add Force Sub:</b>\n\nType <code>/addfsub -100xxxxxx</code> to add a new Force Subscribe channel.",
        "admin_delfsub": "<b>➖ Del Force Sub:</b>\n\nType <code>/delfsub -100xxxxxx</code> to remove a Force Subscribe channel.",
        "admin_listfsub": "<b>📋 List Force Sub:</b>\n\nType <code>/listfsub</code> to view all Force Subscribe channels."
    }

    # Click panna button-kku yetha text-a edukkum
    guide_text = guides.get(data, "Invalid selection.")
    
    # Keela "Back to Menu" button add panrom
    back_btn = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="admin_home")]]
    
    # Message-a pudhu text mtrum back button kooda edit panrom
    await query.message.edit_text(
        text=guide_text,
        reply_markup=InlineKeyboardMarkup(back_btn),
        parse_mode=enums.ParseMode.HTML
    )
