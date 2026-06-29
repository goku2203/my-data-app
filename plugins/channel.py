import asyncio
from pyrogram import Client, filters
from info import CHANNELS, MOVIE_DB_CHANNEL, USER_REQ_DB_CHANNEL, CAM_DB_CHANNEL
from database.ia_filterdb import save_file

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    
    # Rendu DB channel layum file vantha mattum process pannum
    if message.chat.id in [MOVIE_DB_CHANNEL, USER_REQ_DB_CHANNEL, CAM_DB_CHANNEL]:
        
        # Auto-caption bot caption-ah matha 8 seconds time kudukkurom
        await asyncio.sleep(8)
        
        # Telegram kitta irunthu update aana pudhu message-ah thirumbavum ketkom
        try:
            fresh_msg = await bot.get_messages(message.chat.id, message.id)
        except Exception:
            fresh_msg = message # Oruvela error vantha pazhaya message-aye use pannikkum
            
        for file_type in ("document", "video", "audio"):
            media_obj = getattr(fresh_msg, file_type, None)
            if media_obj is not None:
                break
        else:
            return
            
        media_obj.file_type = file_type
        # Puthu caption inga exact-ah kidaichidum
        media_obj.caption = fresh_msg.caption 
        
        await save_file(media_obj)
