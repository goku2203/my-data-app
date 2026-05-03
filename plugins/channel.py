from pyrogram import Client, filters
from info import CHANNELS, MOVIE_DB_CHANNEL, USER_REQ_DB_CHANNEL
from database.ia_filterdb import save_file

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    for file_type in ("document", "video"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return
    media.file_type = file_type
    media.caption = message.caption
    
    # Rendu DB channel layum file vantha save pannum
    if message.chat.id in [MOVIE_DB_CHANNEL, USER_REQ_DB_CHANNEL]:
        await save_file(media)
