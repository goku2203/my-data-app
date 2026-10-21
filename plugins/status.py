import time
import psutil
import asyncio
from datetime import datetime, timezone, timedelta
from pyrogram import Client, filters, enums, raw
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from database.ia_filterdb import Media
from info import ADMINS, BOT_START_TIME
from utils import get_size

# ─────────────────────────────────────────────
#  /stats  &  /status  →  Bot Status Dashboard
#  • Text only (no image)
#  • Buttons: Refresh + Close
#  • Auto-deletes after 10 minutes
# ─────────────────────────────────────────────

AUTO_DELETE_SECONDS = 600          # 10 minutes
MONGO_FREE_LIMIT = 536870912       # 512 MB (Atlas free tier)
IST = timezone(timedelta(hours=5, minutes=30))

# (chat_id, message_id) -> running auto-delete task
_TIMERS = {}


def _bar(percent, size=10):
    """▰▰▰▱▱▱▱▱▱▱ style progress bar"""
    percent = max(0, min(100, percent))
    filled = int(round(percent / 100 * size))
    return "▰" * filled + "▱" * (size - filled)


def _buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Rᴇғʀᴇsʜ", callback_data="status_refresh"),
            InlineKeyboardButton("✖️ Cʟᴏsᴇ", callback_data="status_close"),
        ]
    ])


async def _measure_ping(client):
    """Real Telegram API round-trip time in ms."""
    try:
        t = time.perf_counter()
        await client.invoke(raw.functions.Ping(ping_id=int(time.time())))
        return round((time.perf_counter() - t) * 1000, 1)
    except Exception:
        return 0.0


async def _monthly_verified():
    try:
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return await db.col.count_documents(
            {"verify_status_v2.verify_until": {"$gte": start_of_month}}
        )
    except Exception:
        try:
            return await db.get_verified_count()
        except Exception:
            return 0


async def get_status_text(client, user_mention):
    ping = await _measure_ping(client)

    uptime_sec = int(time.time() - BOT_START_TIME)
    uptime = (
        f"{uptime_sec // 86400}d {(uptime_sec % 86400) // 3600}h "
        f"{(uptime_sec % 3600) // 60}m"
    )

    total_users = await db.total_users_count()
    total_chats = await db.total_chat_count()
    total_files = await Media.collection.count_documents({})
    monthly_verified = await _monthly_verified()

    monsize = await db.get_db_size()
    mongo_percent = (monsize / MONGO_FREE_LIMIT) * 100
    used_str = get_size(monsize)
    free_str = get_size(max(MONGO_FREE_LIMIT - monsize, 0))

    # psutil.cpu_percent(interval=...) blocks, so run it in a thread
    cpu = await asyncio.to_thread(psutil.cpu_percent, 0.5)
    ram = psutil.virtual_memory().percent

    updated = datetime.now(IST).strftime("%I:%M %p")

    text = (
        "<blockquote><b>📡 Bᴏᴛ Sᴛᴀᴛᴜs Dᴀsʜʙᴏᴀʀᴅ</b></blockquote>\n"
        f"<i>Hᴇʏ {user_mention} ✨ ʜᴇʀᴇ's ʏᴏᴜʀ ʟɪᴠᴇ ʙᴏᴛ ʀᴇᴘᴏʀᴛ.</i>\n\n"

        "<b>🤖 Sʏsᴛᴇᴍ Pᴇʀғᴏʀᴍᴀɴᴄᴇ</b>\n"
        "<blockquote>"
        f"⏱️ <b>Uptime</b> ➜ <code>{uptime}</code>\n"
        f"🚀 <b>Ping</b> ➜ <code>{ping} ms</code>"
        "</blockquote>\n"

        "<b>📊 Usᴇʀ Sᴛᴀᴛɪsᴛɪᴄs</b>\n"
        "<blockquote>"
        f"👤 <b>Total Users</b> ➜ <code>{total_users:,}</code>\n"
        f"👥 <b>Total Groups</b> ➜ <code>{total_chats:,}</code>\n"
        f"🗂️ <b>Total Files</b> ➜ <code>{total_files:,}</code>\n"
        f"📅 <b>Monthly Verified</b> ➜ <code>{monthly_verified:,}</code>"
        "</blockquote>\n"

        "<b>💾 Dᴀᴛᴀʙᴀsᴇ (MᴏɴɢᴏDB)</b>\n"
        "<blockquote>"
        f"📈 <b>Used</b> ➜ <code>{used_str}</code> (<code>{mongo_percent:.2f}%</code>)\n"
        f"🟢 <b>Free</b> ➜ <code>{free_str}</code>\n"
        f"<code>{_bar(mongo_percent)}</code>"
        "</blockquote>\n"

        "<b>🖥️ Sᴇʀᴠᴇʀ (Rᴇɴᴅᴇʀ Cʟᴏᴜᴅ)</b>\n"
        "<blockquote>"
        f"⚡ <b>CPU</b> ➜ <code>{cpu}%</code>\n"
        f"<code>{_bar(cpu)}</code>\n"
        f"💽 <b>RAM</b> ➜ <code>{ram}%</code>\n"
        f"<code>{_bar(ram)}</code>"
        "</blockquote>\n"

        f"<i>🕒 Uᴘᴅᴀᴛᴇᴅ: {updated} IST\n
        🗑️ Aᴜᴛᴏ-ᴄʟᴏsᴇ ɪɴ 10 ᴍɪɴ</i>"
    )
    return text


# ── Auto-delete (10 min) ─────────────────────
async def _auto_delete(bot_msg, user_msg):
    try:
        await asyncio.sleep(AUTO_DELETE_SECONDS)
    except asyncio.CancelledError:
        return
    _TIMERS.pop((bot_msg.chat.id, bot_msg.id), None)
    for m in (bot_msg, user_msg):
        try:
            if m:
                await m.delete()
        except Exception:
            pass


def _start_timer(bot_msg, user_msg):
    key = (bot_msg.chat.id, bot_msg.id)
    old = _TIMERS.pop(key, None)
    if old:
        old.cancel()
    _TIMERS[key] = asyncio.create_task(_auto_delete(bot_msg, user_msg))


# ── Commands ─────────────────────────────────
@Client.on_message(filters.command(["stats", "status"]) & filters.user(ADMINS))
async def status_command(client, message):
    tmp = await message.reply_text("<b><i>⏳ Fetching live status...</i></b>", quote=True)
    try:
        text = await get_status_text(client, message.from_user.mention)
    except Exception as e:
        return await tmp.edit_text(f"<b>⚠️ Couldn't fetch status:</b>\n<code>{e}</code>")

    await tmp.edit_text(
        text,
        reply_markup=_buttons(),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
    )
    _start_timer(tmp, message)


# ── Refresh ──────────────────────────────────
@Client.on_callback_query(filters.regex("^status_refresh$") & filters.user(ADMINS))
async def status_refresh(client, query):
    await query.answer("🔄 Refreshing...", show_alert=False)
    try:
        text = await get_status_text(client, query.from_user.mention)
        await query.message.edit_text(
            text,
            reply_markup=_buttons(),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )
        # refresh pannina 10 min timer reset aagum
        _start_timer(query.message, query.message.reply_to_message)
    except Exception:
        # "message is not modified" etc. – ignore
        pass


# ── Close ────────────────────────────────────
@Client.on_callback_query(filters.regex("^status_close$") & filters.user(ADMINS))
async def status_close(client, query):
    key = (query.message.chat.id, query.message.id)
    task = _TIMERS.pop(key, None)
    if task:
        task.cancel()
    try:
        await query.message.delete()
    except Exception:
        pass
    try:
        if query.message.reply_to_message:
            await query.message.reply_to_message.delete()
    except Exception:
        pass
