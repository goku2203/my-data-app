import uvloop
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

# FIX: Create event loop BEFORE importing Pyrogram & use uvloop for speed
uvloop.install()
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

import tgcrypto
from pyrogram import Client, __version__, enums
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, KEEP_ALIVE_URL, DEFAULT_AUTH_CHANNELS, RENDER_URL
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
    return webserver.Response(text="Bot is Running on Render!")

@routes.get("/verify", allow_head=True)
async def verify_route_handler(request):
    code = request.query.get("code", "")
    if not code:
        return webserver.Response(text="Invalid Security Token!", status=400)
        
    try:
        with open("verify.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        html_content = html_content.replace("{{CODE}}", code)
    except Exception as e:
        return webserver.Response(text=f"Error loading verification file: {e}", status=500)
            
    return webserver.Response(text=html_content, content_type="text/html")

async def web_server():
    web_app = webserver.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def preload_auth_channels():
    if not await db.get_auth_channels():
        await db.set_auth_channels(DEFAULT_AUTH_CHANNELS)
        logging.info("Set default AUTH_CHANNELs in DB.")

# REPLACE PANNU:
async def keep_alive():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Koyeb URL-a thavirthu, unga original Render URL-a ping pannum.
                # Ithu unga bot-a sleep aagama 24/7 online-la vechikkum.
                target_url = KEEP_ALIVE_URL if KEEP_ALIVE_URL and "koyeb" not in KEEP_ALIVE_URL else RENDER_URL
                if target_url:
                    await session.get(target_url)
                    logging.info(f"Sent keep-alive request to: {target_url}")
            except Exception as e:
                logging.error(f"Keep-alive request failed: {e}")
            await asyncio.sleep(111)

# Exact-ah 12:00 AM ku bot-a force restart pandra puthu function
async def auto_restart(client):
    while True:
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)
        # Midnight 12:00 AM check
        if now.hour == 0 and now.minute == 0:
            logging.info("Midnight Auto-Restarting...")
            try:
                await client.send_message(
                    chat_id=LOG_CHANNEL, 
                    text="<b>  Midnight System Restarting... Please Wait!</b>", 
                    parse_mode=enums.ParseMode.HTML
                )
            except:
                pass
            # Bot code-a internal ah re-run pandra command
            os.execl(sys.executable, sys.executable, *sys.argv)
        await asyncio.sleep(60) # Ovoru 1 minute-kum time check pannum

class Bot(Client):
    #   INTHA CODE-AH REPLACE PANNU:
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=8,
            plugins={"root": "plugins"},
            sleep_threshold=5,
            max_concurrent_transmissions=5,
        )

    async def start(self, **kwargs):
        # Bot start aagum pothu maintenance status edukka
        temp.MAINT_MODE = await db.get_maintenance()
        
        try:
            self.web_app = webserver.AppRunner(await web_server())
            await self.web_app.setup()
            bind_address = "0.0.0.0"
            self.tcp_site = webserver.TCPSite(self.web_app, bind_address, int(PORT))
            await self.tcp_site.start()
            logging.info(f"  Web Server Started on Port {PORT}")
        except Exception as e:
            logging.error(f"  Web Server Error: {e}")

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
        asyncio.create_task(keep_alive())
        asyncio.create_task(auto_restart(self)) # Ithu thaan puthusa add panna timer task
        logging.info(f"{me.first_name} running on Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)
        
        print("mntg4u</>")

        #   INTHA PUDHU CODE-AH REPLACE PANNU:
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)
        today = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%I:%M:%S %p")
                  
        try:
            # Midnight (12 AM to 2 AM) auto-restart aana detailed message varum, illana simple message varum
            if now.hour in [0, 1]:
                await self.send_message(
                    chat_id=LOG_CHANNEL,
                    text=script.RESTART_GC_TXT.format(today, time_str),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await self.send_message(
                    chat_id=LOG_CHANNEL,
                    text="<b>  Bot is Online!</b>",
                    parse_mode=enums.ParseMode.HTML
                )
        except Exception as e:
            logging.error(f"  LOG_CHANNEL Error: {e}")

    async def stop(self, *args, **kwargs):
        await super().stop(*args, **kwargs)
        logging.info("Bot stopped. Bye.")

    async def iter_messages(self, chat_id: Union[int, str], limit: int, offset: int = 0) -> AsyncGenerator["types.Message", None]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff)))
            for message in messages:
                yield message
                current += 1

if __name__ == "__main__":
    app = Bot()
    app.run()
