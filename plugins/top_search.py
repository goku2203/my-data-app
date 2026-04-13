from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
import random
from info import PICS # Unnoda bot pics edukka

# ==========================================
# EDIT PANRA AREA (Unakku pidicha movies potukko)
# ==========================================
TOP_MOVIES_TEXT = """
<b>🔥 Weekly Top Search Movies 🔥</b>

1. GOAT (The Greatest Of All Time) 🐐
2. Vettaiyan 🕶️
3. Amaran 🎖️
4. Kanguva 🦅
5. Vidaamuyarchi 🏎️

<i>Ithu namma group-la intha vaaram athigama search panna movies!</i>
"""

# ==========================================
# MAIN CODE
# ==========================================
@Client.on_callback_query(filters.regex(r'^top_search$'))
async def top_search_callback(client: Client, query: CallbackQuery):
    # Back button set panrom
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="start_data")]]
    
    # Photo kooda sethu text maara intha code
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=random.choice(PICS),
            caption=TOP_MOVIES_TEXT,
            parse_mode=enums.ParseMode.HTML
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await query.answer()
