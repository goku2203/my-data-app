from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS 

@Client.on_message(filters.private & filters.command("admin") & filters.user(ADMINS))
async def master_admin_panel(bot: Client, message: Message):
    
    # Simple & Fluent English Text
    panel_text = (
        "<b>👑 Master Admin Control Panel</b>\n\n"
        "<i>Welcome! Here is your complete set of admin tools. "
        "Select any option below to manage your bot, database, and channels.</i>"
    )
    
    # Ella 14 Commands-um inga categorize panni buttons aakiyachu
    buttons = [
        # --- System & Core Settings ---
        [
            InlineKeyboardButton("📊 Bot Stats", callback_data="admin_panel"),
            InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton("♻️ Restart Bot", callback_data="admin_restart")
        ],
        
        # --- File Management ---
        [
            InlineKeyboardButton("🗑 Delete Files", callback_data="admin_deletefiles"),
            InlineKeyboardButton("🧹 Clean Cam/PreDVD", callback_data="admin_cleancam")
        ],
        [
            InlineKeyboardButton("🔎 Scan Movie", callback_data="admin_scanmovie"),
            InlineKeyboardButton("🏓 Ping", callback_data="admin_ping")
        ],
        
        # --- Auto-Index Channels Management ---
        [
            InlineKeyboardButton("➕ Add Channel", callback_data="admin_addchannel"),
            InlineKeyboardButton("➖ Del Channel", callback_data="admin_delchannel")
        ],
        [
            InlineKeyboardButton("📋 List All Channels", callback_data="admin_listchannels")
        ],
        
        # --- Force Sub Management ---
        [
            InlineKeyboardButton("➕ Add FSub", callback_data="admin_addfsub"),
            InlineKeyboardButton("➖ Del FSub", callback_data="admin_delfsub")
        ],
        [
            InlineKeyboardButton("📋 List All FSub", callback_data="admin_listfsub")
        ],
        
        # --- Close Button ---
        [
            InlineKeyboardButton("❌ Close Panel", callback_data="close_data")
        ]
    ]
    
    # Fast Execution
    await message.reply_text(
        text=panel_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )
