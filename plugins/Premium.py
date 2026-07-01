import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex("^premium_data$"))
async def premium_callback_handler(client: Client, query: CallbackQuery):
    payment_link = "https://upi.pe/gokula8@ibl" 
    admin_link = "https://t.me/Screenshot_gk_bot" 
    plan_image = "https://i.ibb.co/YFFY84YX/photo.jpg"
    
    caption = (
        "<b>💎 PREMIUM PLANS & PRICING 💎</b>\n\n"
        "Do you want to use the bot <b>Without Ads</b> and in <b>High Speed</b>?\n"
        "Select one of the plans below! 👇\n\n"
        "<blockquote><b>🔥 CHEAPEST PRICES:</b>\n"
        "✨ <b>1 Day:</b> ₹9 Only\n"
        "✨ <b>7 Days:</b> ₹59 Only\n"
        "✨ <b>24 Months:</b> ₹99 Only (Best Offer! 🤩)</blockquote>\n\n"
        "<b>💡 How to Pay?</b>\n"
        "1. Click the <b>'Pay Now'</b> button below.\n"
        "2. Make the payment and take a <b>Screenshot</b>.\n"
        "3. Click <b>'Send Screenshot'</b> and send it to the Admin.\n\n"
        "<i>✅ Premium will be activated once the verification is done!</i>"
    )
    
    buttons = [
        [
            InlineKeyboardButton("💳 Pay Now / QR Code", url=payment_link),
            InlineKeyboardButton("🧾 Send Screenshot", url=admin_link)
        ],
        [
            InlineKeyboardButton("🔙 Home", callback_data="start_data"),
            InlineKeyboardButton("❌ Close", callback_data="close_data")
        ]
    ]
    
    await query.message.edit_media(
        media=InputMediaPhoto(media=plan_image, caption=caption),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return await query.answer()
