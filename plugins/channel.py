from pyrogram import Client, filters
from info import CHANNELS
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
    # --- INGA MAATHUNGA ---
    
    # Unga Backup Tamil Movie Channel ID & Pudhu User Request DB ID
    MOVIE_CHANNEL_ID = -1001999941677
    USER_REQ_DB_ID = -100xxxxxxx # Unnoda pudhu DB channel ID
    
    # Condition: Idhu Movie Channel illana User Req Channel-a iruntha mattum save pannu
    if message.chat.id in [MOVIE_CHANNEL_ID, USER_REQ_DB_ID]:
        await save_file(media)
    
    # Anime channel-a iruntha 'save_file' run aagathu, so update-um pogathu.
