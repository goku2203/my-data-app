import re
import logging
import asyncio
import os
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Union, List
import base64
import urllib.parse

from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid, ChatAdminRequired, ChannelInvalid, ChannelPrivate, ChatIdInvalid
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import enums
from pyrogram.enums import ChatMemberStatus

from imdb import IMDb

from info import LONG_IMDB_DESCRIPTION, MAX_LIST_ELM, VERIFY_EXPIRE, IS_VERIFY, SHORTLINK_URL, SHORTLINK_API, REQUEST_FSUB_MODE, RENDER_URL, LOG_CHANNEL
from database.users_chats_db import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

imdb = IMDb('http') 

BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)
JOIN_REQUEST_USERS = {}

# temp db for banned 
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT=int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    SETTINGS = {}
    MAINT_MODE = False  # Itha puthusa add pannunga


async def is_subscribed(user_id: int, client) -> bool:
    # Ellaa FSub channel-layum (member illana join request) irukkanum
    return not await get_missing_channels(user_id, client)

# ==========================================
# 🔐 FORCE SUB CORE (cache + safe checks)
# ==========================================
FSUB_OK = "ok"
FSUB_MISSING = "missing"
FSUB_BROKEN = "broken"      # bot admin illa / channel delete aachu -> user-a block pannama skip

FSUB_OK_TTL = 90            # join aana user-a 90 sec cache (group-la flood API calls thadukka)
FSUB_LINK_TTL = 6 * 3600    # invite link 6 hours cache (ovvoru click-kum puthu link create panna koodathu)
FSUB_ALERT_GAP = 3600       # same broken channel alert 1 hour-ku oru thadava mattum

_AUTH_CACHE = {"ts": 0.0, "data": []}
_OK_CACHE = {}              # user_id -> expiry time
_LINK_CACHE = {}            # channel_id -> (url, request_mode, created_ts)
_TITLE_CACHE = {}           # channel_id -> title
_ALERT_CACHE = {}           # channel_id -> last alert ts
_LINK_LOCK = asyncio.Lock()

_JOINED_MARK = set()        # (user_id, channel) -> indha user channel-la irundhaanga (memory copy)

async def mark_joined(user_id: int, channel):
    """User channel-la member-a irukkaanga nu note pannum (apram leave panna detect panna)."""
    if (user_id, channel) in _JOINED_MARK:
        return
    if len(_JOINED_MARK) > 20000:
        _JOINED_MARK.clear()
    _JOINED_MARK.add((user_id, channel))
    try:
        await db.mark_joined(user_id, channel)
    except Exception as e:
        logger.error(f"[FSUB] mark_joined failed: {e}")

async def forget_membership(user_id: int, channel):
    """User channel-a LEAVE pannitaanga -> join request / joined / cache ellam clear. Next time FSub page varum."""
    _JOINED_MARK.discard((user_id, channel))
    JOIN_REQUEST_USERS.get(user_id, set()).discard(channel)
    _OK_CACHE.pop(user_id, None)
    try:
        await db.remove_join_request(user_id, channel)
        await db.unmark_joined(user_id, channel)
    except Exception as e:
        logger.error(f"[FSUB] forget_membership failed: {e}")

async def get_auth_channels_cached(force: bool = False) -> list:
    now = time.time()
    if not force and now - _AUTH_CACHE["ts"] < 30:
        return _AUTH_CACHE["data"]
    data = await db.get_auth_channels()
    _AUTH_CACHE["data"] = list(data)
    _AUTH_CACHE["ts"] = now
    return _AUTH_CACHE["data"]

def invalidate_fsub_cache(links: bool = True, channel=None):
    """Channel add / delete pannina apram call pannanum - ellaarukkum puthu list udane apply aagum."""
    _AUTH_CACHE["ts"] = 0.0
    _OK_CACHE.clear()
    if links:
        if channel is None:
            _LINK_CACHE.clear()
        else:
            _LINK_CACHE.pop(channel, None)

async def get_channel_title(client, channel) -> str:
    title = _TITLE_CACHE.get(channel)
    if title:
        return title
    try:
        chat = await client.get_chat(channel)
        title = chat.title or "Channel"
        _TITLE_CACHE[channel] = title
        return title
    except Exception:
        return "Channel"

async def _alert_broken(client, channel, reason):
    now = time.time()
    if now - _ALERT_CACHE.get(channel, 0) < FSUB_ALERT_GAP:
        return
    _ALERT_CACHE[channel] = now
    logger.error(f"[FSUB] Channel {channel} problem: {reason}")
    try:
        await client.send_message(
            LOG_CHANNEL,
            f"<b>⚠️ FSub Channel Problem</b>\n\n<b>Channel:</b> <code>{channel}</code>\n<b>Reason:</b> <code>{reason}</code>\n\n"
            "<i>Bot-a antha channel-la admin aakkunga (Invite Users permission-oda). Appo varaikkum antha channel skip aagum, users block aaga maattanga.</i>",
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        pass

async def get_invite_link(client, channel, force: bool = False):
    """Oru channel-ku invite link (cache-oda). Fail aanaa None."""
    now = time.time()
    cached = _LINK_CACHE.get(channel)
    if cached and not force and cached[1] == REQUEST_FSUB_MODE and now - cached[2] < FSUB_LINK_TTL:
        return cached[0]

    reason = "unknown"
    async with _LINK_LOCK:
        cached = _LINK_CACHE.get(channel)
        if cached and not force and cached[1] == REQUEST_FSUB_MODE and time.time() - cached[2] < FSUB_LINK_TTL:
            return cached[0]
        for attempt in range(2):
            try:
                invite = await client.create_chat_invite_link(
                    channel,
                    creates_join_request=REQUEST_FSUB_MODE,
                    name="BotFSub"
                )
                _LINK_CACHE[channel] = (invite.invite_link, REQUEST_FSUB_MODE, time.time())
                return invite.invite_link
            except FloodWait as e:
                reason = f"FloodWait {e.value}s"
                if attempt == 0 and e.value <= 10:
                    await asyncio.sleep(e.value + 1)
                    continue
                break
            except Exception as e:
                reason = f"invite link create failed: {type(e).__name__}"
                break
    await _alert_broken(client, channel, reason)
    return None

async def create_invite_links(client) -> dict:
    """{channel_id: url} - cache irukkurathunaala fast, API spam illa."""
    channels = await get_auth_channels_cached()
    if not channels:
        return {}
    results = await asyncio.gather(*[get_invite_link(client, ch) for ch in channels])
    return {ch: url for ch, url in zip(channels, results) if url}

async def get_poster(query, bulk=False, id=False, file=None):
    if not id:
        # https://t.me/GetTGLink/4183
        query = (query.strip()).lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1]) 
        else:
            year = None
        movieid = imdb.search_movie(title.lower(), results=10)
        if not movieid:
            return None
        if year:
            filtered=list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid=list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid
        movieid = movieid[0].movieID
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer":list_to_str(movie.get("writer")),
        "producer":list_to_str(movie.get("producer")),
        "composer":list_to_str(movie.get("composer")) ,
        "cinematographer":list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url':f'https://www.imdb.com/title/tt{movieid}'
    }

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id}-Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} -Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        return False, "Error"

# ==========================================
# 🕒 GLOBAL AUTO DELETE + FILE LINK PREFIX HELPERS
# Link prefix:  file | filep   (p = protected)
# Auto delete time ELLAATHUKKUM oru global setting (DB-la permanent).
# ==========================================
AUTO_DELETE_CYCLE = [5, 10, 30]
_PRE_REGEX = re.compile(r"^file(p?)(\d*)$")

def build_pre(settings):
    return 'filep' if settings.get('file_secure') else 'file'

def parse_pre(pre):
    """Prefix-a (protect_content, ignored) aaga maathum. Pazhaya 'file10' maadhiri links-um work aagum (number ignore aagum)."""
    m = _PRE_REGEX.match(pre or "")
    if not m:
        return False, None
    return bool(m.group(1)), None

def auto_delete_label(ad):
    if not ad.get('enabled'):
        return "❌ Off"
    return f"⏳ {int(ad.get('time', 5))} Min"

def next_auto_delete(ad):
    cur = int(ad.get('time', 5)) if ad.get('enabled') else None
    if cur in AUTO_DELETE_CYCLE:
        return AUTO_DELETE_CYCLE[(AUTO_DELETE_CYCLE.index(cur) + 1) % len(AUTO_DELETE_CYCLE)]
    return AUTO_DELETE_CYCLE[0]

def build_settings_markup(settings, grp_id, ad):
    """/settings command-um, button click-um rendu idathulayum same markup. ad = global autodelete settings."""
    g = str(grp_id)
    def row(label, key, text):
        cb = f'setgs#{key}#{settings[key]}#{g}'
        return [InlineKeyboardButton(label, callback_data=cb), InlineKeyboardButton(text, callback_data=cb)]
    yn = lambda k: '✅ Yes' if settings[k] else '❌ No'
    ad_cb = f'setad#{g}'
    return InlineKeyboardMarkup([
        row('Filter Button', 'button', 'Single' if settings['button'] else 'Double'),
        row('Bot PM', 'botpm', yn('botpm')),
        row('File Secure', 'file_secure', yn('file_secure')),
        row('IMDB', 'imdb', yn('imdb')),
        row('Spell Check', 'spell_check', yn('spell_check')),
        row('Welcome', 'welcome', yn('welcome')),
        [InlineKeyboardButton('Auto Delete File', callback_data=ad_cb),
         InlineKeyboardButton(auto_delete_label(ad), callback_data=ad_cb)],
        [InlineKeyboardButton("❌ Close", callback_data="close_data")],
    ])

async def get_settings(group_id):
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        temp.SETTINGS[group_id] = settings
    return settings
    
async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current[key] = value
    temp.SETTINGS[group_id] = current
    await db.update_settings(group_id, current)
    
def get_size(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
        
    # Puthu condition: MB-kku decimal vendaam, mathathukku venum
    if units[i] == "MB":
        return f"{int(round(size))} MB"
    else:
        return "%.2f %s" % (size, units[i])

def get_file_id(msg: Message):
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj

def extract_user(message: Message) -> Union[int, str]:
    """extracts the user from a message"""
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if (
            len(message.entities) > 1 and
            message.entities[1].type == enums.MessageEntityType.TEXT_MENTION
        ):
            
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    key = remove_escapes(text[1:counter].strip())
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def parser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])

        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except:
        return note_data, buttons, None

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


async def get_short(link):
    # Shortener Website URL connect panrom
    shortener_url = f"https://{SHORTLINK_URL}/api"
    params = {'api': SHORTLINK_API, 'url': link}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(shortener_url, params=params, raise_for_status=True) as response:
                data = await response.json()
                # Server response-la irunthu short link edukkurom
                return data["shortenedUrl"]
    except Exception as e:
        print(f"Shortener Error: {e}")
        return link # Error vantha original link return aagirum

# ----- START OF NEW UTILS CODE -----

async def get_verify_link(user_id, file_id=None):
    bot_username = temp.U_NAME if temp.U_NAME else "Mikasa_Lovely_bot"
         
    if file_id:
        link = f"https://telegram.me/{bot_username}?start=verify_{user_id}_{file_id}"
    else:
        link = f"https://telegram.me/{bot_username}?start=verify_{user_id}"
             
    encoded_link = urllib.parse.quote(link)
    api_url = f"https://{SHORTLINK_URL}/api?api={SHORTLINK_API}&url={encoded_link}&format=text"
         
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    short_link = await response.text()
                else:
                    short_link = link
    except Exception as e:
        print(f"Shortener URL Error: {e}")
        short_link = link

    # Arolinks URL-a Base64 la hide panni unga Render Verify Page-kku anuppurom
    try:
        clean_short_link = short_link.strip().strip('"').strip("'")
        if clean_short_link.startswith("{"):
            try:
                import json
                js = json.loads(clean_short_link)
                clean_short_link = js.get("shortenedUrl", clean_short_link)
            except Exception:
                pass
        if not clean_short_link.startswith("http"):
            clean_short_link = link

        encoded_url = base64.urlsafe_b64encode(clean_short_link.encode('utf-8')).decode('utf-8').rstrip('=')
        
        # Unga exact Render URL inga hardcode panniyachu (Entha error-um varathu)
        render_base_url = RENDER_URL
            
        return f"{render_base_url}/verify?code={encoded_url}"
    except Exception as e:
        print(f"Verify Route Error: {e}")
        return short_link

async def verify_user(user_id):
    # Admin set panna hours ah DB la irunthu edukkum
    settings = await db.get_verify_settings()
    hours = settings['hours']
    expiry = datetime.now() + timedelta(hours=hours)
    
    await db.col.update_one({'id': user_id}, {'$set': {'verify_status_v2': {'is_verified': True, 'verify_until': expiry}}}, upsert=True)
    await db.add_verified_user()
    return settings # Settings ah return pandrom success message kku

async def check_verification(client, user_id):
    if not IS_VERIFY: return True
    
    settings = await db.get_verify_settings()
    if settings['mode'] == 'everytime':
        return False # Everytime mode on la iruntha always false
        
    user = await db.col.find_one({'id': user_id})
    if not user: return False
    
    verify_status = user.get('verify_status_v2', {})
    expiry = verify_status.get('verify_until')
    
    if expiry and datetime.now() < expiry:
        return True # Time mudiyala na access kedaikkum
        
    return False

# ----- PUTHUSA ADD PANNA FUNCTION (get_clean_size) -----
def get_clean_size(size):
    if not size:
        return "Unknown Size"
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}B"

# ----- END -----

async def _channel_state(user_id: int, channel, client) -> str:
    """ok = member / join-request anuppiyirukkaanga | missing = join pannala | broken = channel check panna mudiyala (skip)"""
    not_member = False  # Telegram urudhi-aa "member illa" nu sonna mattum True (temporary error-ku False)
    for attempt in range(2):
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                if REQUEST_FSUB_MODE:
                    await mark_joined(user_id, channel)  # join aanaanga nu note - apram leave panna theriyum
                return FSUB_OK
            not_member = True
            break  # LEFT / BANNED -> member illa
        except UserNotParticipant:
            not_member = True
            break  # normal - join pannala / leave pannitaanga
        except FloodWait as e:
            if attempt == 0 and e.value <= 5:
                await asyncio.sleep(e.value + 1)
                continue
            return FSUB_MISSING
        except (ChatAdminRequired, ChannelInvalid, ChannelPrivate, ChatIdInvalid) as e:
            await _alert_broken(client, channel, type(e).__name__)
            return FSUB_BROKEN
        except PeerIdInvalid:
            # user peer problem-aa channel problem-aa nu paakkurom
            try:
                await client.get_chat(channel)
            except Exception as e:
                await _alert_broken(client, channel, f"PeerIdInvalid/{type(e).__name__}")
                return FSUB_BROKEN
            break
        except Exception as e:
            logger.warning(f"[FSUB] get_chat_member error ch={channel} user={user_id}: {type(e).__name__}: {e}")
            break

    if REQUEST_FSUB_MODE:
        # 🚪 Munnadi join aagi (request approve / member) ippo channel-la illa = LEAVE pannitaanga
        #    -> pazhaya join request-a kanakku edukka koodathu, FSub page thirumba varanum
        if not_member:
            try:
                left = (user_id, channel) in _JOINED_MARK or await db.was_joined(user_id, channel)
            except Exception:
                left = False
            if left:
                await forget_membership(user_id, channel)
                return FSUB_MISSING
        if channel in JOIN_REQUEST_USERS.get(user_id, set()):
            return FSUB_OK
        # Bot restart aana memory poidum, so DB-la paakkurom
        try:
            if await db.has_join_request(user_id, channel):
                JOIN_REQUEST_USERS.setdefault(user_id, set()).add(channel)
                return FSUB_OK
        except Exception as e:
            logger.error(f"Join request DB check failed: {e}")
    return FSUB_MISSING

async def get_missing_channels(user_id: int, client, use_cache: bool = True) -> list:
    now = time.time()
    if use_cache and _OK_CACHE.get(user_id, 0) > now:
        return []
    auth_channels = await get_auth_channels_cached()
    if not auth_channels:
        return []
    # Ellaa channels-um orey nerathula (parallel) check pannum, so fast
    states = await asyncio.gather(*[_channel_state(user_id, ch, client) for ch in auth_channels])
    missing = [ch for ch, st in zip(auth_channels, states) if st == FSUB_MISSING]
    if not missing:
        if len(_OK_CACHE) > 5000:
            _OK_CACHE.clear()
        _OK_CACHE[user_id] = now + FSUB_OK_TTL
    return missing

# Inga unga thevaiyillatha varthaigalai add pannikkonga
JUNK_WORDS = [
    "goku_stark",
    "goku stark",
    "goku",
    "tamil rockers",
    "tamilrockers",
    "grouplinkstamil",
    "Team_HDT",
    "cinema_company",
    "Filmbox_Studios",
    "Goku_Stark"
]

# Pattern Compilation (Super Fast Speed kku)
_escaped_words = [re.escape(word) for word in JUNK_WORDS]
# Auto @username remover idhula update aagirukku
_escaped_words.append(r"@[a-zA-Z0-9_]+")
JUNK_PATTERN = re.compile(r"(" + "|".join(_escaped_words) + r")", flags=re.IGNORECASE)

# Master Clean Function (Ultimate Setup)
def clean_filename(name):
    if not name: return ""
    
    # 1. '-Stark' ah perfectly remove panra step
    cleaned = re.sub(r'(?i)[-\s]*Stark[\s]*', ' ', name)
    
    # 2. THE BRAHMASTRA: '@' la aaramikkira FULL peraiyum thookidum!
    cleaned = re.sub(r'(?i)@[^\s\[\]\(\)]+', '', cleaned)
    
    # 3. Matha junk words (goku_stark, filmbox_studios ellam)
    cleaned = JUNK_PATTERN.sub("", cleaned)
    
    # 4. Starting & ending la irukka thevaiyillatha symbols ah clean panni tharum
    return re.sub(r"^[_\-\s\[\]\(\)]+|[_\-\s\[\]\(\)]+$", "", cleaned).strip()
