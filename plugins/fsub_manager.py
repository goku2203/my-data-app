import asyncio
import html
import logging
import os
import re
import time

from pyrogram import Client, filters, enums
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.users_chats_db import db
from info import ADMINS, REQUEST_FSUB_MODE
from utils import (
    JOIN_REQUEST_USERS,
    create_invite_links,
    get_auth_channels_cached,
    get_invite_link,
    get_missing_channels,
    invalidate_fsub_cache,
    mark_joined,
    forget_membership,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ==========================================================
#  ⚙️ FSUB SETTINGS (indha file-la thaan maathanum - Render env-la kooda maathalaam)
# ==========================================================
FSUB_PM_TTL = int(os.environ.get("FSUB_PM_TTL", 600))          # PM prompt evvalavu seconds irukkum
FSUB_GROUP_TTL = int(os.environ.get("FSUB_GROUP_TTL", 180))    # Group prompt evvalavu seconds irukkum
FSUB_DONE_DELETE = int(os.environ.get("FSUB_DONE_DELETE", 10)) # "Joined" small message auto delete (seconds)
FSUB_POLL_SECONDS = int(os.environ.get("FSUB_POLL_SECONDS", 8))# event miss aana safety check interval

# ==========================================================
#  🎨 FSUB DESIGN  (text only - image illa)
#  Font  : Small-Caps  |  Style : Blockquote + status list
# ==========================================================
_SC = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")


def sc(text: str) -> str:
    """normal text -> ꜱᴍᴀʟʟ ᴄᴀᴘꜱ font"""
    return text.lower().translate(_SC)


def _short(title: str, limit: int = 26) -> str:
    title = (title or "Channel").strip()
    return title if len(title) <= limit else title[: limit - 1] + "…"


def _prompt_text(mention: str, rows: list) -> str:
    """rows = [(title_html, joined_bool), ...]"""
    lines = []
    for title, joined in rows:
        lines.append(f"✅  <s>{title}</s>" if joined else f"❌  <b>{title}</b>")
    status = "\n".join(lines)

    text = (
        f"<b>🔒 {sc('access locked')}</b>\n\n"
        f"<blockquote>👋 {mention}, {sc('join all the channels below to unlock this bot')}.</blockquote>\n\n"
        f"<b>📋 {sc('required channels')}</b>\n"
        f"{status}\n\n"
    )
    if REQUEST_FSUB_MODE:
        text += f"<i>📨 {sc('tap request to join - no need to wait for approval')}.</i>\n"
    text += f"<i>⚡ {sc('access unlocks automatically after you join')}.</i>"
    return text


def _done_text(mention: str) -> str:
    return (
        f"<blockquote><b>✅ {sc('joined successfully')}!</b></blockquote>\n"
        f"<i>{mention} • {sc('access unlocked')} ⚡</i>"
    )


# ==========================================================
#  📦 PENDING PROMPTS (memory-la mattum - chinna & fast)
# ==========================================================
class _Pending:
    __slots__ = ("client", "prompt", "mention", "resume", "created", "missing", "last_check", "busy", "group", "triggers")

    def __init__(self, client, prompt, mention, resume, missing, group, trigger=None):
        self.client = client
        self.prompt = prompt
        self.triggers = [trigger] if trigger is not None else []  # user-oda message(s) - expire aanaa delete aagum
        self.mention = mention
        self.resume = resume
        self.missing = list(missing)
        self.group = group
        self.created = time.time()
        self.last_check = time.time()
        self.busy = False


PENDING = {}  # (chat_id, user_id) -> _Pending
_POLLER = None


async def _delete(msg):
    try:
        if msg:
            await msg.delete()
    except Exception:
        pass


async def _delete_later(msg, delay):
    await asyncio.sleep(delay)
    await _delete(msg)


async def _build(client, mention: str, missing_set: set):
    """text + buttons ready pannum. Channel name kaattaama "Channel 1, 2.." nu kaattum. Join pannathathukku mattum button varum."""
    channels = await get_auth_channels_cached()
    links = await create_invite_links(client)
    shown = [ch for ch in channels if ch in links]

    rows, buttons = [], []
    for num, ch in enumerate(shown, start=1):  # number fixed - join panna channel number maaraadhu
        joined = ch not in missing_set
        rows.append((f"{sc('channel')} {num}", joined))
        if not joined:
            icon, word = ("📨", sc("request")) if REQUEST_FSUB_MODE else ("📢", sc("join"))
            buttons.append([InlineKeyboardButton(f"{icon} {word} {sc('channel')} {num}", url=links[ch])])
    return _prompt_text(mention, rows), InlineKeyboardMarkup(buttons)


# ==========================================================
#  🚪 MAIN GATE  -  PM /start, PM text, GROUP text, AUTOPOST link ellaathukkum itha thaan use pannum
# ==========================================================
async def fsub_gate(client, message, resume=None) -> bool:
    """
    True  = user join pannala -> FSub page kaattitten (caller stop aaganum)
    False = ellaa channel-um joined -> caller normal-aa continue pannalaam

    resume = async function (no args). User join pannina udane automatic-aa call aagum
             (PM-la file/verify flow, group-la search).
    """
    user = message.from_user
    if not user or user.is_bot:
        return False

    key = (message.chat.id, user.id)
    is_group = message.chat.type != enums.ChatType.PRIVATE

    pend = PENDING.get(key)
    if pend:
        # already prompt irukku -> latest request-a remember pannikko
        if resume:
            pend.resume = resume
        if await _refresh(client, key):
            return True  # idhukulla join pannittaanga -> resume already run aagum
        if is_group:
            if len(pend.triggers) < 20:
                pend.triggers.append(message)  # indha message-um expire aanaa delete aagum
            return True  # group-la spam panna koodathu, same prompt-ae irukkattum
        # PM-la: pazhaya prompt-a delete panni, puthusa keezha kaattu
        old = PENDING.pop(key, None)
        if old:
            await _delete(old.prompt)
            resume = resume or old.resume

    missing = await get_missing_channels(user.id, client)
    if not missing:
        return False
    links = await create_invite_links(client)
    missing = [ch for ch in missing if ch in links]  # link create aagatha channel-a skip (user block aaga koodathu)
    if not missing:
        return False

    mention = user.mention
    text, markup = await _build(client, mention, set(missing))

    try:
        sent = await message.reply_text(
            text,
            quote=is_group,
            reply_markup=markup,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except Exception:
        try:
            sent = await client.send_message(
                message.chat.id, text,
                reply_markup=markup,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error(f"[FSUB] prompt send failed: {e}")
            return False

    PENDING[key] = _Pending(client, sent, mention, resume, missing, is_group, trigger=message if is_group else None)
    _ensure_poller()
    return True


# ==========================================================
#  🔄 AUTO CHECK  (join event -> udane | event miss aanaa -> poller)
# ==========================================================
async def _complete(client, key, pend):
    chat_id, _ = key
    await _delete(pend.prompt)

    try:
        done = await client.send_message(
            chat_id, _done_text(pend.mention),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )
        asyncio.create_task(_delete_later(done, FSUB_DONE_DELETE))  # 10 sec-la auto delete
    except Exception as e:
        logger.error(f"[FSUB] done message failed: {e}")

    if pend.resume:
        asyncio.create_task(_run_resume(pend.resume))


async def _run_resume(resume):
    try:
        await resume()
    except Exception as e:
        logger.exception(f"[FSUB] resume failed: {e}")


async def _refresh(client, key) -> bool:
    """True = user ellaa channel-um join pannittaanga (complete aachu)."""
    pend = PENDING.get(key)
    if not pend or pend.busy:
        return False
    pend.busy = True
    try:
        pend.last_check = time.time()
        missing = await get_missing_channels(key[1], client, use_cache=False)
        links = await create_invite_links(client)
        missing = [ch for ch in missing if ch in links]

        if not missing:
            if PENDING.pop(key, None) is pend:
                await _complete(client, key, pend)
            return True

        if set(missing) != set(pend.missing):
            # oru channel join pannitaanga -> ✅ kaattitu button remove pannum
            pend.missing = missing
            text, markup = await _build(client, pend.mention, set(missing))
            try:
                await pend.prompt.edit_text(
                    text, reply_markup=markup,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except MessageNotModified:
                pass
            except Exception as e:
                logger.warning(f"[FSUB] prompt edit failed: {e}")
        return False
    except Exception as e:
        logger.exception(f"[FSUB] refresh error: {e}")
        return False
    finally:
        pend.busy = False


async def refresh_user(client, user_id: int):
    """Join event / join request vantha udane call pannum."""
    for key in [k for k in list(PENDING) if k[1] == user_id]:
        await _refresh(client, key)


def _ensure_poller():
    global _POLLER
    if _POLLER is None or _POLLER.done():
        _POLLER = asyncio.create_task(_poller())


async def _poller():
    """Safety net: event miss aanaalum (bot admin illa, etc.) auto-detect aagum. Expired prompts delete aagum."""
    sem = asyncio.Semaphore(5)

    async def _one(k):
        pend = PENDING.get(k)
        if not pend:
            return
        async with sem:
            await _refresh(pend.client, k)

    while True:
        await asyncio.sleep(max(3, FSUB_POLL_SECONDS))
        try:
            now = time.time()
            due = []
            for key, pend in list(PENDING.items()):
                ttl = FSUB_GROUP_TTL if pend.group else FSUB_PM_TTL
                if now - pend.created > ttl:
                    if PENDING.pop(key, None) is pend:
                        await _delete(pend.prompt)
                        for m in pend.triggers:      # join pannala -> user message-um delete
                            await _delete(m)
                    continue
                due.append(key)
            if due:
                await asyncio.gather(*[_one(k) for k in due])
        except Exception as e:
            logger.exception(f"[FSUB] poller error: {e}")


@Client.on_chat_member_updated(group=11)
async def fsub_member_update(client, update):
    """FSub channel-la user JOIN / LEAVE aana udane (bot antha channel-la admin-a irukkanum)."""
    try:
        if update.chat.type == enums.ChatType.PRIVATE:
            return
        old, new = update.old_chat_member, update.new_chat_member
        user = (new.user if new and new.user else None) or (old.user if old and old.user else None)
        if not user or user.is_bot:
            return
        if update.chat.id not in await get_auth_channels_cached():
            return  # FSub channel illa -> cheap exit

        in_status = (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
        joined_now = bool(new and new.status in in_status)

        if joined_now:
            if REQUEST_FSUB_MODE:
                await mark_joined(user.id, update.chat.id)
            if any(k[1] == user.id for k in PENDING):
                await refresh_user(client, user.id)
        else:
            # 🚪 LEAVE / KICK / BAN -> join request + cache clear (FSub page thirumba varum)
            await forget_membership(user.id, update.chat.id)
    except Exception as e:
        logger.error(f"[FSUB] member update error: {e}")


@Client.on_callback_query(filters.regex(r"^checksub"))
async def legacy_checksub(client, query):
    """Pazhaya 'Try Again' button-a click panninaa (old messages)."""
    await query.answer(f"{sc('this button is old')} - {sc('open your file link again')} 🔄", show_alert=True)
    await _delete(query.message)


# ==========================================================
#  👑 ADMIN COMMANDS  (/addfsub  /delfsub  /listfsub  /fsubrefresh)
# ==========================================================
async def _auto_delete_helper(bot_msg, user_msg, delay=30):
    await asyncio.sleep(delay)
    await _delete(bot_msg)
    await _delete(user_msg)


def _reply_later(k, message, delay):
    asyncio.create_task(_auto_delete_helper(k, message, delay))


async def _resolve_channel(client, arg: str):
    arg = arg.strip()
    if re.fullmatch(r"-?\d+", arg):
        target = int(arg)
    else:
        m = re.search(r"(?:t\.me/|telegram\.me/)([A-Za-z0-9_]{4,})", arg)
        target = m.group(1) if m else arg.lstrip("@")
    return await client.get_chat(target)


@Client.on_message(filters.command("addfsub") & filters.private & filters.user(ADMINS))
async def add_fsub_channel(client, message):
    if len(message.command) < 2:
        k = await message.reply("<b>Usage:</b> <code>/addfsub -100xxxxxxxxxx</code> (or <code>@username</code>)", parse_mode=enums.ParseMode.HTML)
        return _reply_later(k, message, 15)

    try:
        chat = await _resolve_channel(client, message.command[1])
    except Exception as e:
        k = await message.reply(f"❌ <b>Channel kidaikkala:</b> <code>{type(e).__name__}</code>\nBot-a first antha channel-la admin aakkunga.", parse_mode=enums.ParseMode.HTML)
        return _reply_later(k, message, 20)

    channel_id = chat.id
    channels = list(await db.get_auth_channels())
    if channel_id in channels:
        k = await message.reply("ℹ️ Indha channel already FSub list-la irukku.")
        return _reply_later(k, message, 15)

    # --- Bot-ku vela seiyuma nu mudhalayae test pannidrom ---
    try:
        me = await client.get_chat_member(channel_id, "me")
        if me.status != ChatMemberStatus.ADMINISTRATOR:
            raise ValueError("bot admin illa")
    except Exception:
        k = await message.reply("❌ <b>Bot antha channel-la admin illa.</b>\nAdmin aakkitu (Invite Users permission-oda) thirumba try pannunga.", parse_mode=enums.ParseMode.HTML)
        return _reply_later(k, message, 25)

    link = await get_invite_link(client, channel_id, force=True)
    if not link:
        k = await message.reply("❌ <b>Invite link create panna mudiyala.</b>\nBot-ku <b>Invite Users via Link</b> permission kudunga.", parse_mode=enums.ParseMode.HTML)
        return _reply_later(k, message, 25)

    channels.append(channel_id)
    await db.set_auth_channels(channels)
    invalidate_fsub_cache(links=False)  # list refresh + ellarukkum puthu channel udane apply

    k = await message.reply(
        f"✅ <b>FSub Channel Added</b>\n\n<b>Name:</b> {html.escape(chat.title or 'Channel')}\n<b>ID:</b> <code>{channel_id}</code>\n<b>Total:</b> <code>{len(channels)}</code>\n\n"
        "<i>Ippo irundhu ellaa users-um (verified users-um) indha channel-ayum join pannanum. Group, PM, autopost ellathulayum auto apply.</i>",
        parse_mode=enums.ParseMode.HTML,
    )
    _reply_later(k, message, 30)


@Client.on_message(filters.command("delfsub") & filters.private & filters.user(ADMINS))
async def remove_fsub_channel(client, message):
    if len(message.command) < 2:
        k = await message.reply("<b>Usage:</b> <code>/delfsub -100xxxxxxxxxx</code>", parse_mode=enums.ParseMode.HTML)
        return _reply_later(k, message, 15)

    arg = message.command[1]
    channels = list(await db.get_auth_channels())
    channel_id = None
    if re.fullmatch(r"-?\d+", arg):
        channel_id = int(arg)
    else:
        try:
            channel_id = (await _resolve_channel(client, arg)).id
        except Exception:
            pass

    if channel_id not in channels:
        k = await message.reply("ℹ️ Indha channel FSub list-la illa.")
        return _reply_later(k, message, 15)

    channels.remove(channel_id)
    await db.set_auth_channels(channels)
    invalidate_fsub_cache(links=True, channel=channel_id)
    # indha channel-ku wait pannitu irundha prompts-ellam udane refresh aagum
    for uid in {k[1] for k in list(PENDING)}:
        asyncio.create_task(refresh_user(client, uid))

    k = await message.reply(f"🗑️ <b>FSub Channel Removed</b>\n<b>ID:</b> <code>{channel_id}</code>\n<b>Total:</b> <code>{len(channels)}</code>", parse_mode=enums.ParseMode.HTML)
    _reply_later(k, message, 30)


@Client.on_message(filters.command("listfsub") & filters.private & filters.user(ADMINS))
async def list_fsub_channels(client, message):
    channels = await get_auth_channels_cached(force=True)
    if not channels:
        k = await message.reply("ℹ️ FSub channel onnum set pannala.")
        return _reply_later(k, message, 15)

    text = f"<b>📝 Current FSub Channels</b>  <code>({len(channels)})</code>\n\n"
    for ch in channels:
        try:
            chat = await client.get_chat(ch)
            me = await client.get_chat_member(ch, "me")
            ok = me.status == ChatMemberStatus.ADMINISTRATOR
            name = html.escape(chat.title or "Channel")
            state = "✅ Bot Admin" if ok else "⚠️ Bot admin illa"
        except Exception:
            name, state = "Unknown Channel", "❌ Bot access illa"
        text += f"➜ <b>{name}</b>\n   <code>{ch}</code> • {state}\n"
    text += f"\n<i>Mode: {'Join Request' if REQUEST_FSUB_MODE else 'Direct Join'}</i>"

    k = await message.reply(text, parse_mode=enums.ParseMode.HTML)
    _reply_later(k, message, 60)


@Client.on_message(filters.command("fsubrefresh") & filters.private & filters.user(ADMINS))
async def refresh_fsub_links(client, message):
    """Invite link revoke pannina / maathanum-na - puthu links create aagum."""
    invalidate_fsub_cache(links=True)
    links = await create_invite_links(client)
    k = await message.reply(f"🔄 FSub links refresh aachu: <code>{len(links)}</code> channel(s)", parse_mode=enums.ParseMode.HTML)
    _reply_later(k, message, 20)


@Client.on_message(filters.command("clear_join_users") & filters.user(ADMINS))
async def clear_join_users(_, message):
    JOIN_REQUEST_USERS.clear()
    await db.clear_join_requests()
    invalidate_fsub_cache(links=False)
    await message.reply_text("✅ Cleared all join request users.")
