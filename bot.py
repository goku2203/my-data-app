import logging
import logging.config
import os
import sys
import asyncio
from datetime import date, datetime
import pytz
import aiohttp
from aiohttp import web as webserver 

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.CRITICAL - 1)

# 👇 FIX: Create event loop BEFORE importing Pyrogram
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

import tgcrypto
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, KEEP_ALIVE_URL, DEFAULT_AUTH_CHANNELS
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script
from os import environ

# Peer ID invalid fix
from pyrogram import utils as pyroutils
pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

PORT = environ.get("PORT", "8080")

routes = webserver.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return webserver.json_response("Bot is Running on Render!")

async def web_server():
    web_app = webserver.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def preload_auth_channels():
    if not await db.get_auth_channels():
        await db.set_auth_channels(DEFAULT_AUTH_CHANNELS)
        logging.info("Set default AUTH_CHANNELs in DB.")

async def keep_alive():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                if KEEP_ALIVE_URL:
                    await session.get(KEEP_ALIVE_URL)
                    logging.info("Sent keep-alive request.")
            except Exception as e:
                logging.error(f"Keep-alive request failed: {e}")
            await asyncio.sleep(111)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=6,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def kulasthree(self):
        while True:
            await asyncio.sleep(24 * 60 * 60)
            logging.info("✅ Bot is Online and Running!")
            try:
                # Restart-ku bathila verum Online status update anuppum
                await self.send_message(chat_id=LOG_CHANNEL, text="✅ **Daily Status:** Bot is Online and Running normally! 🚀")
            except:
                pass
            # Inga iruntha os.execl line-a thookiyachu, so bot switch off aagathu!

    async def start(self, **kwargs):
        # Bot start aagum pothu maintenance status edukka
        temp.MAINT_MODE = await db.get_maintenance()
        try:
            app = webserver.AppRunner(await web_server())
            await app.setup()
            bind_address = "0.0.0.0"
            await webserver.TCPSite(app, bind_address, int(PORT)).start()
            logging.info(f"✅ Web Server Started on Port {PORT}")
        except Exception as e:
            logging.error(f"❌ Web Server Error: {e}")

        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username

        await preload_auth_channels()

        logging.info(f"{me.first_name} running on Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)
        
        try:
            await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT)
        except Exception as e:
            logging.error(f"⚠️ LOG_CHANNEL Error: Bot is not Admin in Log Channel! Error: {e}")

        print("mntg4u</>")

        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time_str = now.strftime("%H:%M:%S %p")
        
        try:
            await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_GC_TXT.format(today, time_str))
        except Exception:
            pass

        asyncio.create_task(self.kulasthree())
        if KEEP_ALIVE_URL:
            asyncio.create_task(keep_alive())

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

    async def iter_messages(self, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

if __name__ == "__main__":
    app = Bot()
    app.run()
