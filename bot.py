import uvloop
import logging
import logging.config
import os
import sys
import asyncio
import json
import re
from datetime import date, datetime, timedelta, timezone
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
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, KEEP_ALIVE_URL, DEFAULT_AUTH_CHANNELS, RENDER_URL, ADMINS
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

@routes.get("/health", allow_head=True)
async def health_route_handler(request):
    return webserver.Response(text="OK")

_VERIFY_HTML = None
_CODE_OK = re.compile(r"^[A-Za-z0-9+/=_\- ]{8,4000}$")

def _load_verify_html():
    global _VERIFY_HTML
    if _VERIFY_HTML is None:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify.html"), "r", encoding="utf-8") as f:
            _VERIFY_HTML = f.read()
    return _VERIFY_HTML

@routes.get("/verify", allow_head=True)
async def verify_route_handler(request):
    code = request.query.get("code", "")
    if not code or not _CODE_OK.match(code):
        return webserver.Response(text="Invalid Security Token!", status=400)
    try:
        html_content = _load_verify_html()
    except Exception as e:
        return webserver.Response(text=f"Error loading verification file: {e}", status=500)
    return webserver.Response(
        text=html_content,
        content_type="text/html",
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
            "X-Robots-Tag": "noindex, nofollow",
        },
    )

async def web_server():
    web_app = webserver.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def preload_auth_channels():
    if not await db.get_auth_channels():
        await db.set_auth_channels(DEFAULT_AUTH_CHANNELS)
        logging.info("Set default AUTH_CHANNELs in DB.")

# ---------------- KEEP ALIVE + RENDER HOURS ALERT ----------------
# RENDER_HOURS_ALERT    : intha hours-ku mela pona LOG_CHANNEL + ADMINS-ku alert (default 700)
# RENDER_HOURS_LIMIT    : Render free limit (default 750)
# RENDER_OTHER_SERVICES : same Render account-la 24/7 odura vera free service count (default 0)
PING_EVERY = 240  # seconds

async def _send_hours_alert(bot, used_hours, limit):
    left = max(limit - used_hours, 0)
    text = (
        "<b>\u26a0\ufe0f Render Free Hours Alert</b>\n\n"
        f"Intha month use aana hours: <b>{used_hours:.1f} / {limit:.0f}</b>\n"
        f"Meedham iruppadhu: <b>{left:.1f} hrs</b> (approx)\n\n"
        "Limit mudinja Render ella free service-um suspend pannidum. "
        "Munnadiye vera Render account-la deploy panna ready aagu, illa paid plan-ku maaru.\n\n"
        "<i>Note: ithu bot-oda own counter (approx). Exact value Render dashboard > Billing-la paaru.</i>"
    )
    targets = [LOG_CHANNEL] + [a for a in ADMINS if isinstance(a, int)]
    for chat in targets:
        try:
            await bot.send_message(chat, text, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            logging.error(f"Hours alert send failed for {chat}: {e}")

async def _track_hours(bot):
    """Ovvoru ping-kum 240s add pannum, threshold thaandina oru thadava alert anuppum."""
    alert_at = float(environ.get("RENDER_HOURS_ALERT", "700"))
    limit = float(environ.get("RENDER_HOURS_LIMIT", "750"))
    others = int(environ.get("RENDER_OTHER_SERVICES", "0"))
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    meta = db.db.meta
    add = PING_EVERY * (1 + others)

    doc = await meta.find_one_and_update(
        {"_id": "render_hours", "month": month},
        {"$inc": {"seconds": add}},
        return_document=True,
    )
    if doc is None:  # puthu month (illa first time) -> reset
        await meta.replace_one(
            {"_id": "render_hours"},
            {"_id": "render_hours", "month": month, "seconds": add, "alerted": False},
            upsert=True,
        )
        doc = await meta.find_one({"_id": "render_hours"})

    used_hours = doc["seconds"] / 3600
    if used_hours >= alert_at and not doc.get("alerted"):
        await _send_hours_alert(bot, used_hours, limit)
        await meta.update_one({"_id": "render_hours"}, {"$set": {"alerted": True}})

async def keep_alive(bot):
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                target_url = RENDER_URL or environ.get("RENDER_EXTERNAL_URL", "")
                if target_url:
                    target_url = target_url.rstrip("/") + "/health"
                    async with session.get(target_url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        await resp.read()
                    logging.info(f"Sent keep-alive request to: {target_url}")
            except Exception as e:
                logging.error(f"Keep-alive request failed: {e}")
            try:
                await _track_hours(bot)
            except Exception as e:
                logging.error(f"Hours tracking failed: {e}")
            await asyncio.sleep(PING_EVERY)

# ---------------- MIDNIGHT AUTO RESTART (FIXED) ----------------
# Restart pannum pothu "Midnight System Restarting" message id-a intha file la save pannuvom.
# Process restart aanalum file irukkum (same container), so puthu process ithai paathu
# antha old message-a delete pannidum.
RESTART_FLAG = "restart_flag.json"
IST = pytz.timezone('Asia/Kolkata')

def _read_flag():
    try:
        with open(RESTART_FLAG, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _write_flag(data):
    try:
        with open(RESTART_FLAG, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        logging.error(f"Flag write failed: {e}")

def _clear_flag():
    try:
        os.remove(RESTART_FLAG)
    except FileNotFoundError:
        pass
    except Exception as e:
        logging.error(f"Flag remove failed: {e}")

async def auto_restart(client):
    while True:
        now = datetime.now(IST)
        # Next midnight (naalaikku 12:00 AM) varaikkum thookkam
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        await asyncio.sleep((next_midnight - now).total_seconds() + 1)

        today = datetime.now(IST).strftime("%Y-%m-%d")
        flag = _read_flag()
        # Innaikku already restart aaiduchu na thirumba restart pannaathey (loop guard)
        if flag and flag.get("date") == today:
            continue

        logging.info("Midnight Auto-Restarting...")
        msg_id = None
        try:
            m = await client.send_message(
                chat_id=LOG_CHANNEL,
                text="<b>Midnight System Restarting... Please Wait!</b>",
                parse_mode=enums.ParseMode.HTML
            )
            msg_id = m.id
        except Exception as e:
            logging.error(f"Restart notice failed: {e}")

        _write_flag({"date": today, "pending": True, "chat_id": LOG_CHANNEL, "msg_id": msg_id})
        os.execl(sys.executable, sys.executable, *sys.argv)

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
        # Web server mudhalla start aagatum - Render port detect panna
        try:
            self.web_app = webserver.AppRunner(await web_server())
            await self.web_app.setup()
            bind_address = "0.0.0.0"
            self.tcp_site = webserver.TCPSite(self.web_app, bind_address, int(PORT))
            await self.tcp_site.start()
            logging.info(f"  Web Server Started on Port {PORT}")
        except Exception as e:
            logging.error(f"  Web Server Error: {e}")

        # Bot start aagum pothu maintenance status edukka
        temp.MAINT_MODE = await db.get_maintenance()
        
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
        asyncio.create_task(keep_alive(self))
        asyncio.create_task(auto_restart(self)) # Ithu thaan puthusa add panna timer task
        logging.info(f"{me.first_name} running on Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)
        
        print("mntg4u</>")

        now = datetime.now(IST)
        today = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%I:%M:%S %p")

        flag = _read_flag()
        try:
            if flag and flag.get("pending"):
                # Midnight auto-restart: "Restarting..." message-a delete pannitu details anuppu
                if flag.get("msg_id"):
                    try:
                        await self.delete_messages(flag["chat_id"], flag["msg_id"])
                    except Exception as e:
                        logging.error(f"Old restart msg delete failed: {e}")
                await self.send_message(
                    chat_id=LOG_CHANNEL,
                    text=script.RESTART_GC_TXT.format(today, time_str),
                    parse_mode=enums.ParseMode.HTML
                )
                # pending=False pannidrom; date mattum irukkattum (innaikku thirumba restart aagama irukka)
                _write_flag({"date": flag.get("date"), "pending": False, "chat_id": None, "msg_id": None})
            else:
                await self.send_message(
                    chat_id=LOG_CHANNEL,
                    text="<b>✅ Bot is Online!</b>",
                    parse_mode=enums.ParseMode.HTML
                )
        except Exception as e:
            logging.error(f"LOG_CHANNEL Error: {e}")

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
