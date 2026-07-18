import asyncio
import re
import math
import time
import difflib
import psutil
import logging
import random
import ast
from datetime import datetime

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty, ButtonUrlInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid

# --- Missing aana mukkiyamana imports inga add panni irukken ---
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import find_filter, get_filters
from Script import script
from info import HYPER_MODE, ADMINS, CUSTOM_FILE_CAPTION, IMDB_TEMPLATE, MISSING_LOG_CHANNEL, WAIT_STICKERS
from utils import get_size, is_subscribed, get_poster, temp, get_settings, create_invite_links, clean_filename

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BUTTONS = {}
SPELL_CHECK = {}

LOG_COOLDOWN = 600
RECENT_REQUESTS = {}

# Regex compile panna CPU save aagum
JUNK_WORDS_LIST = ["1080p", "720p", "480p", "tamil dubbed", "tamil", "telugu", "hindi", "malayalam", "dubbed", "hq", "hd", "print", "download", "movie", "full"]
JUNK_REGEX = re.compile(r'(?i)\b(' + '|'.join(JUNK_WORDS_LIST) + r')\b')

SPAM_WORDS_LIST = ["porn", "p_o_r_n", "slut", "booty", "anal", "pussy", "dick", "boobs", "whore", "cum", "cuming", "lesbian", "fettish", "creampie", "sex"]

async def auto_delete_msgs(bot_msg, user_msg, delay):
    await asyncio.sleep(delay)
    
    async def delete_msg(msg):
        try:
            if msg:
                await msg.delete()
        except:
            pass
            
    # Rendu message-um exact-a ore nerathula delete aaga idhu help pannum
    await asyncio.gather(
        delete_msg(bot_msg),
        delete_msg(user_msg)
    )

@Client.on_message((filters.group | filters.private) & filters.text & ~filters.regex(r"^[/\.]"))
async def give_filter(client, message):
         
    # Ippo Private & Group rendukkum Fsub check aagum
    if not await is_subscribed(message.from_user.id, client):
        from plugins.fsub_manager import send_fsub_prompt
        await send_fsub_prompt(client, message)
        return
        
    k = await manual_filters(client, message)
    if k == False:
        await auto_filter(client, message)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("**Search for Yourself**🔎", show_alert=True)

    try:
        offset = int(offset)
    except:
        offset = 0

    search = BUTTONS.get(key)
    if not search:
        await query.answer(script.OLD_MES, show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return

    # Movie name vachu group panni, Low MB to High GB sort pannum
    files.sort(key=lambda x: (x.file_name.lower(), x.file_size if x.file_size else 0), reverse=False)

    settings = await get_settings(query.message.chat.id)
    if not settings:
        settings = {"button": True, "botpm": False, "file_secure": False, "imdb": False, "spell_check": False, "template": IMDB_TEMPLATE, "welcome": False}

    if HYPER_MODE:
        cap_lines = []
        for file in files:
            file_link = f"https://t.me/{temp.U_NAME}?start=file_{file.file_id}"
            disp_name = clean_filename(file.file_name) 
            cap_lines.append(f"📁 {get_size(file.file_size)} - [{disp_name}]({file_link})")
        cap_text = "\n".join(cap_lines)
        btn = []
    else:
        if settings['button']:
            btn = []
            for file in files:
                disp_name = clean_filename(file.file_name)
                if not disp_name or disp_name.lower() == "none":
                    disp_name = clean_filename(getattr(file, "caption", "")) or "Unknown File"
                btn.append([
                    InlineKeyboardButton(
                        text=f"📂[{get_size(file.file_size)}] ➵ {disp_name}", callback_data=f'files#{file.file_id}'
                    )
                ])
        else:
            btn = []
            for file in files:
                disp_name = clean_filename(file.file_name)
                if not disp_name or disp_name.lower() == "none":
                    disp_name = clean_filename(getattr(file, "caption", "")) or "Unknown File"
                btn.append([
                    InlineKeyboardButton(
                        text=f"{disp_name}", callback_data=f'files#{file.file_id}'
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}", callback_data=f'files_#{file.file_id}'
                    )
                ])

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10

    if n_offset == 0 or len(files) < 10:
        btn.append(
            [
                InlineKeyboardButton("◀️ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages")
            ]
        )
    elif off_set is None:
        btn.append(
            [
                InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ▶️", callback_data=f"next_{req}_{key}_{n_offset}")
            ]
        )
    else:
        btn.append(
            [
                InlineKeyboardButton("◀️ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"📃 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ▶️", callback_data=f"next_{req}_{key}_{n_offset}")
            ]
        )

    btn.append([InlineKeyboardButton("📝 Request Movie 📝", url="https://t.me/Tamilmovieslink_bot")])
    
    try:
        if HYPER_MODE:
            await query.edit_message_text(
                text=cap_text,
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        else:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
    except MessageNotModified:
        pass

    await query.answer()

@Client.on_callback_query(filters.regex(r"^spol")) 
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("Search for Yourself🔎", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
        
    if not query.message.reply_to_message:
        return await query.answer("Original message has been deleted!", show_alert=True)
        
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_MES, show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer(script.CHK_MOV_ALRT)
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit(script.MOV_NT_FND)
            asyncio.create_task(auto_delete_msgs(k, query.message.reply_to_message, 10))

@Client.on_callback_query(filters.regex(r"^(close_data|alertmessage|file|checksub|pages|esp|msp|hsp|tsp)"))
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()

    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)

    elif query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        
        title = clean_filename(files.file_name)
        size = get_size(files.file_size)
        f_caption = clean_filename(files.caption)
        
        settings = await get_settings(query.message.chat.id)
        if not settings:
             settings = {"button": True, "botpm": False, "file_secure": False, "imdb": False, "spell_check": False, "template": IMDB_TEMPLATE, "welcome": False}

        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"

        try:
            if not await is_subscribed(query.from_user.id, client):
                invite_links = await create_invite_links(client)
                first_link = next(iter(invite_links.values()), f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                await query.answer(url=first_link)
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")

    elif query.data.startswith("checksub"):
        if not await is_subscribed(query.from_user.id, client):
            await query.answer("I Like Your Smartness, But Don't Be Oversmart", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
            
        await query.answer()
        await client.send_message(query.from_user.id, "Please request from Bot PM.")

    elif query.data == "pages":
        await query.answer()

    elif query.data == "esp":
        await query.answer(text=script.ENG_SPELL, show_alert="true")
    elif query.data == "msp":
        await query.answer(text=script.MAL_SPELL, show_alert="true")
    elif query.data == "hsp":
        await query.answer(text=script.HIN_SPELL, show_alert="true")
    elif query.data == "tsp":
        await query.answer(text=script.TAM_SPELL, show_alert="true")

async def auto_filter(client, msg, spoll=False):
    # Maintenance Check for Groups & Bot PM
    if temp.MAINT_MODE and msg.from_user.id not in ADMINS:
        k = await msg.reply_text(script.MAINT_TXT, parse_mode=enums.ParseMode.HTML)
        asyncio.create_task(auto_delete_msgs(k, msg, 30))
        return
    try:
        if not spoll:
            message = msg
            settings = await get_settings(message.chat.id)
            
            if not settings:
                settings = {"button": True, "botpm": False, "file_secure": False, "imdb": False, "spell_check": False, "template": IMDB_TEMPLATE, "welcome": False}

            if message.text.startswith("/"): return
            if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
                return
            
            if 2 < len(message.text) < 100:
                search = message.text
                
                # JUNK WORDS REMOVER (Using Global Regex)
                search = JUNK_REGEX.sub('', search).strip()
                
                # SPAM FILTER
                is_spam = False
                search_lower = search.lower()
                
                if "@" in search_lower or "http" in search_lower or "t.me" in search_lower:
                    is_spam = True
                else:
                    for word in SPAM_WORDS_LIST:
                        if word in search_lower:
                            is_spam = True
                            break
                            
                if is_spam:
                    return
                
                # info.py la irunthu random aaga oru sticker eduthu anuppum
                search_msg = await message.reply_sticker(
                    sticker=random.choice(WAIT_STICKERS)
                )
                
                # Sticker play aaga mudhalla 1.5 seconds wait pandrom
                await asyncio.sleep(1.5)
                
                # Athukappuram thaan background-la theda (search panna) start pandrom
                files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
                
                if not files:
                    clean_query = search.lower()
                    current_time = time.time()
                    
                    if clean_query not in RECENT_REQUESTS or (current_time - RECENT_REQUESTS.get(clean_query, 0)) >= LOG_COOLDOWN:
                        RECENT_REQUESTS[clean_query] = current_time
                        user_mention = message.from_user.mention if message.from_user else 'Anonymous'
                        user_id = message.from_user.id if message.from_user else 'Unknown'
                        
                        # NEW: Generate clickable link for Source Chat
                        if message.chat.type == enums.ChatType.PRIVATE:
                            source_link = "Bot PM"
                        else:
                            chat_title = message.chat.title or "Unknown"
                            if getattr(message.chat, "username", None):
                                source_link = f"<a href='https://t.me/{message.chat.username}'>{chat_title}</a>"
                            else:
                                chat_id_str = str(message.chat.id).replace("-100", "")
                                source_link = f"<a href='https://t.me/c/{chat_id_str}/1'>{chat_title}</a>"
                        
                        # FIX: Corrected the order (User Name, User ID, Query, Source Chat Link)
                        log_msg = script.MISSING_LOG_TXT.format(user_mention, user_id, search, source_link)
                        
                        if MISSING_LOG_CHANNEL:
                            try:
                                await client.send_message(
                                    chat_id=MISSING_LOG_CHANNEL, 
                                    text=log_msg, 
                                    disable_web_page_preview=True
                                )
                            except Exception as e:
                                print(f"Missing Log Error: {e}")
                    
                    if settings["spell_check"]:
                        await search_msg.delete() 
                        return await advantage_spell_chok(client, msg)
                        
                    else:
                        req_btn = [[InlineKeyboardButton("📝 Request Movie", url="https://t.me/Tamilmovieslink_bot")]]
                        await search_msg.delete() 
                        
                        not_found_msg = await message.reply_text(
                            text=script.SPOLL_NOT_FND.format(search=search),
                            reply_markup=InlineKeyboardMarkup(req_btn)
                        )
                        asyncio.create_task(auto_delete_msgs(not_found_msg, msg, 15))
                        return
                else:
                    await search_msg.delete() 
        else:
            settings = await get_settings(msg.message.chat.id)
            if not settings:
                 settings = {"button": True, "botpm": False, "file_secure": False, "imdb": False, "spell_check": False, "template": IMDB_TEMPLATE, "welcome": False}
            
            message = msg.message.reply_to_message or msg.message
            search, files, offset, total_results = spoll

        if files:
            files.sort(key=lambda x: (x.file_name.lower(), x.file_size if x.file_size else 0), reverse=False)

        pre = 'filep' if settings['file_secure'] else 'file'

        if HYPER_MODE:
            cap_lines = []
            for file in files:
                disp_name = clean_filename(file.file_name)
                if not disp_name or disp_name.lower() == "none":
                    disp_name = clean_filename(getattr(file, "caption", "")) or "Unknown File"
                file_link = f"https://t.me/{temp.U_NAME}?start={pre}_{file.file_id}"
                cap_lines.append(f"📁 {get_size(file.file_size)} - [{disp_name}]({file_link})")
            cap_text = "\n".join(cap_lines)

            btn = []
            if offset != "" and len(files) >= 10:
                key = f"{message.chat.id}-{message.id}"
                BUTTONS[key] = search
                req = message.from_user.id if message.from_user else 0
                btn.append([
                    InlineKeyboardButton(text=f"📃 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
                    InlineKeyboardButton(text="NEXT ▶️", callback_data=f"next_{req}_{key}_{offset}")
                ])
            else:
                btn.append([InlineKeyboardButton(text="📃 1/1", callback_data="pages")])

        else:
            if settings["button"]:
                btn = []
                for file in files:
                    disp_name = clean_filename(file.file_name)
                    if not disp_name or disp_name.lower() == "none":
                        disp_name = clean_filename(getattr(file, "caption", "")) or "Unknown File"
                    btn.append([
                        InlineKeyboardButton(
                            text=f"📁 [{get_size(file.file_size)}] ➵ {disp_name}", 
                            url=f"https://t.me/{temp.U_NAME}?start={pre}_{file.file_id}"
                        )
                    ])
            else:
                btn = []
                for file in files:
                    disp_name = clean_filename(file.file_name)
                    if not disp_name or disp_name.lower() == "none":
                        disp_name = clean_filename(getattr(file, "caption", "")) or "Unknown File"
                    btn.append([
                        InlineKeyboardButton(
                            text=f"{disp_name}",
                            url=f"https://t.me/{temp.U_NAME}?start={pre}_{file.file_id}"
                        ),
                        InlineKeyboardButton(
                            text=f"{get_size(file.file_size)}",
                            url=f"https://t.me/{temp.U_NAME}?start={pre}_{file.file_id}"
                        ),
                    ])
                    
            if offset != "":
                key = f"{message.chat.id}-{message.id}"
                BUTTONS[key] = search
                req = message.from_user.id if message.from_user else 0
                btn.append([
                    InlineKeyboardButton(text=f"📃 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
                    InlineKeyboardButton(text="NEXT ▶️", callback_data=f"next_{req}_{key}_{offset}")
                ])
            else:
                btn.append([InlineKeyboardButton(text="📃 1/1", callback_data="pages")])
                
        btn.append([InlineKeyboardButton("📝 Request Movie 📝", url="https://t.me/Tamilmovieslink_bot")])
        
        imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
        TEMPLATE = settings['template']
        if imdb:
            cap = TEMPLATE.format(
                query=search,
                title=imdb['title'],
                votes=imdb['votes'],
                aka=imdb["aka"],
                seasons=imdb["seasons"],
                box_office=imdb['box_office'],
                localized_title=imdb['localized_title'],
                kind=imdb['kind'],
                imdb_id=imdb["imdb_id"],
                cast=imdb["cast"],
                runtime=imdb["runtime"],
                countries=imdb["countries"],
                certificates=imdb["certificates"],
                languages=imdb["languages"],
                director=imdb["director"],
                writer=imdb["writer"],
                producer=imdb["producer"],
                composer=imdb["composer"],
                cinematographer=imdb["cinematographer"],
                music_team=imdb["music_team"],
                distributors=imdb["distributors"],
                release_date=imdb['release_date'],
                year=imdb['year'],
                genres=imdb['genres'],
                poster=imdb['poster'],
                plot=imdb['plot'],
                rating=imdb['rating'],
                url=imdb['url'],
                **locals()
            )
        else:
            mention = message.from_user.mention if message.from_user else "User"
            cap = script.RESULT_TXT.format(mention=mention, query=search)

        if imdb and imdb.get('poster'):
            try:
                if not spoll: await search_msg.delete()
                delauto = await message.reply_photo(
                    photo=imdb.get('poster'),
                    caption=cap[:1024],
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                asyncio.create_task(auto_delete_msgs(delauto, message, 60))
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                if not spoll: await search_msg.delete()
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                delau = await message.reply_photo(
                    photo=poster,
                    caption=cap[:1024],
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                asyncio.create_task(auto_delete_msgs(delau, message, 60))
            except Exception as e:
                if not spoll: await search_msg.delete()
                audel = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
                asyncio.create_task(auto_delete_msgs(audel, message, 60))
        else:
            if not spoll: await search_msg.delete()
            
            if HYPER_MODE:
                autodel = await message.reply_text(
                    cap_text,
                    reply_markup=InlineKeyboardMarkup(btn),
                    parse_mode=enums.ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
            else:
                autodel = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))

            asyncio.create_task(auto_delete_msgs(autodel, message, 60))

        if spoll:
            await msg.message.delete()
            
    except ButtonUrlInvalid:
        logger.error("BUTTON URL INVALID ERROR: Kaila podra link sariya illa, check pannunga.")
    except Exception as final_error:
        logger.exception(f"CRITICAL ERROR IN AUTO_FILTER: {final_error}")

async def advantage_spell_chok(client, msg):
    mv_id = msg.id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0
    
    settings = await get_settings(msg.chat.id)
    if not settings:
         settings = {"button": True, "botpm": False, "file_secure": False, "imdb": False, "spell_check": False, "template": IMDB_TEMPLATE, "welcome": False}

    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)
    
    query = query.strip()
    
    if query:
        search_query = query + " movie"
    else:
        search_query = msg.text

    try:
        movies = await get_poster(search_query, bulk=True)
    except Exception as e:
        logger.exception(e)
        movies = None

    movielist = []
    
    if movies:
        movielist += [movie.get('title') for movie in movies]

    if not movielist:
        try:
            first_char = query[0] if query else ""
            if first_char:
                cursor = Media.collection.find({"file_name": {"$regex": f"^{first_char}", "$options": "i"}}).sort("$natural", -1).limit(3000)
                db_files = await cursor.to_list(length=3000)
                db_names = [clean_filename(x['file_name']) for x in db_files] 
                db_names = list(set(db_names)) 
                if db_names:
                    matches = difflib.get_close_matches(query, db_names, n=5, cutoff=0.5)
                    movielist += matches
        except Exception as e:
            logger.error(f"Fuzzy Error: {e}")
    
    if not movielist:
        reqst_gle = mv_rqst.replace(" ", "+")
        google_btn = [
            [InlineKeyboardButton('  Check on Google  ', url=f"https://www.google.com/search?q={reqst_gle}")]
        ]
        k = await msg.reply_text(
            text=script.SPOLL_NOT_FND, 
            reply_markup=InlineKeyboardMarkup(google_btn),
            reply_to_message_id=msg.id
        )
        asyncio.create_task(auto_delete_msgs(k, msg, 60))
        return
        
    movielist = list(dict.fromkeys(movielist)) 
    
    SPELL_CHECK[mv_id] = movielist
    
    btn = [
        [
            InlineKeyboardButton(
                text=movie_name.strip(),
                callback_data=f"spol#{reqstr1}#{k}",
            )
        ]
        for k, movie_name in enumerate(movielist)
    ]
    
    btn.append([InlineKeyboardButton(text="✖ Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])
    
    spell_check_del = await msg.reply_text(
        text=f"<b>❌ Couldn't find '<code>{mv_rqst}</code>'\n\nDid you mean any of these? 👇</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        reply_to_message_id=msg.id
    )
    
    asyncio.create_task(auto_delete_msgs(spell_check_del, msg, 180))

async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
