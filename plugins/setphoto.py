import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
from pyrogram.enums import ParseMode
from info import ADMINS, UPDATES_CHANNEL
from plugins.autopost import POST_CAPTIONS, LAST_POST

logger = logging.getLogger(__name__)

# Auto Delete Helper Function
async def auto_delete_helper(bot_msg, user_msg, delay=15):
    await asyncio.sleep(delay)
    try:
        if bot_msg: await bot_msg.delete()
    except:
        pass
    try:
        if user_msg: await user_msg.delete()
    except:
        pass

@Client.on_message(
    filters.private & filters.photo & filters.user(ADMINS)
    & filters.regex(r"^(/setphoto|/set|/sp)")
)
async def set_post_photo(client, message):
    try:
        parts = message.caption.split()
        
        # Link kudutha antha post, illana kadaisi autopost
        if len(parts) > 1:
            post_id = int(parts[1].rstrip("/").split("/")[-1])
        else:
            post_id = LAST_POST.get("id")
        
        if not post_id:
            msg = await message.reply("⚠️ Post ID not found. Please provide the post link.")
            asyncio.create_task(auto_delete_helper(msg, message, 15))
            return
        
        # Original caption iruntha athai use pannum
        caption = POST_CAPTIONS.get(post_id)
        if not caption:
            old = await client.get_messages(UPDATES_CHANNEL, post_id)
            if not old or not old.caption:
                msg = await message.reply("⚠️ Post not found.")
                asyncio.create_task(auto_delete_helper(msg, message, 15))
                return
            caption = old.caption.html
        
        await client.edit_message_media(
            chat_id=UPDATES_CHANNEL,
            message_id=post_id,
            media=InputMediaPhoto(
                message.photo.file_id,
                caption=caption,
                parse_mode=ParseMode.HTML,
            ),
        )
        msg = await message.reply("✅ Photo updated successfully!")
        asyncio.create_task(auto_delete_helper(msg, message, 15))
        
    except Exception as e:
        logger.error(f"setphoto error: {e}", exc_info=True)
        msg = await message.reply(f"⚠️ Error: {e}")
        asyncio.create_task(auto_delete_helper(msg, message, 15))
