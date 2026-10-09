import logging
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
from pyrogram.enums import ParseMode
from info import ADMINS, UPDATES_CHANNEL

logger = logging.getLogger(__name__)

@Client.on_message(
    filters.private & filters.photo & filters.user(ADMINS)
    & filters.regex(r"^/setphoto\s+\S+")
)
async def set_post_photo(client, message):
    try:
        link = message.caption.split()[1]
        post_id = int(link.rstrip("/").split("/")[-1])

        old = await client.get_messages(UPDATES_CHANNEL, post_id)
        if not old or not old.caption:
            return await message.reply("❌ Post kidaikkala, link check pannunga.")

        await client.edit_message_media(
            chat_id=UPDATES_CHANNEL,
            message_id=post_id,
            media=InputMediaPhoto(
                message.photo.file_id,
                caption=old.caption.html,
                parse_mode=ParseMode.HTML,
            ),
        )
        await message.reply("✅ Photo maathiyaachu!")
    except Exception as e:
        logger.error(f"setphoto error: {e}", exc_info=True)
        await message.reply(f"❌ Error: {e}")
