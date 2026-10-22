#  @MrMNTG @MusammilN
import logging
from pyrogram import Client
from pyrogram.types import ChatJoinRequest
from database.users_chats_db import db
from utils import JOIN_REQUEST_USERS

@Client.on_chat_join_request()
async def join_request_handler(client, update: ChatJoinRequest):
    user_id = update.from_user.id
    chat_id = update.chat.id

    auth_channels = await db.get_auth_channels()
    if chat_id in auth_channels:
        if user_id not in JOIN_REQUEST_USERS:
            JOIN_REQUEST_USERS[user_id] = set()
        JOIN_REQUEST_USERS[user_id].add(chat_id)
        try:
            await db.add_join_request(user_id, chat_id)
        except Exception as e:
            logging.error(f"Join request save failed: {e}")

        # Join request anuppina udane FSub page automatic-aa complete aagum
        try:
            from plugins.fsub_manager import refresh_user
            await refresh_user(client, user_id)
        except Exception as e:
            logging.error(f"FSub auto refresh failed: {e}")

#  @MrMNTG @MusammilN
