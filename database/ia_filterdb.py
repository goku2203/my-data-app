#  @MrMNTG @MusammilN
#please give credits https://github.com/MN-BOTS/ShobanaFilterBot

import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, USE_CAPTION_FILTER
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME

async def save_file(media):
    """Save file in database"""
    # TODO: Find better way to get same file_id for same media to avoid duplicates
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    # Fix: Handle Pyrogram string caption error safely
    cap_text = getattr(media, "caption", None)
    if cap_text and hasattr(cap_text, "html"):
        cap_text = cap_text.html
    elif cap_text:
        cap_text = str(cap_text)

    try:
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=cap_text,
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            logger.warning(
                f'{getattr(media, "file_name", "NO_FILE")} is already saved in database'
            )
            # If file already exists, update its caption so search works perfectly
            if cap_text:
                await Media.collection.update_one({'_id': file_id}, {'$set': {'caption': cap_text}})
            return False, 0
        else:
            logger.info(f'{getattr(media, "file_name", "NO_FILE")} is saved to database')
            return True, 1

async def get_search_results(query, file_type=None, max_results=10, offset=0, filter=False):
    """3-Level Powerful Search Engine"""
    query = query.strip()
    
    # 1. Thevai illatha junk words-a thookiduvom (Updated list)
    junk_words = r"\b(movie|movies|download|tamil|telugu|malayalam|hindi|english|dubbed|hd|hq|1080p|720p|480p|4k|print|full|file|link|send|give|please|plz|bro|pro|sir|update)\b"
    clean_query = re.sub(junk_words, "", query, flags=re.IGNORECASE).strip()
    
    # FIX: Remove brackets () [] from query so that Year searches match accurately
    clean_query = re.sub(r'[\[\]\(\)\{\}]', ' ', clean_query).strip()
    clean_query = re.sub(r'\s+', ' ', clean_query).strip()
    
    if not clean_query:
        clean_query = query

    keywords = clean_query.split()
    if not keywords:
        raw_pattern = '.'
    else:
        raw_pattern = "".join([f"(?=.*{re.escape(word)})" for word in keywords])
        
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return [], '', 0

    # FIX: Unga idea padi epavume Filename & Caption check aaganum
    filter_db = {'$or': [{'file_name': regex}, {'caption': regex}]}
    
    if file_type:
        filter_db['file_type'] = file_type

    # LEVEL 1: Normal Exact Search
    total_results = await Media.count_documents(filter_db)

    # LEVEL 2: FUZZY SEARCH (For Spelling Mistakes like 'mester', 'masterr')
    if total_results == 0:
        fuzzy_keywords = []
        for word in keywords:
            word = re.escape(word) # Special characters error varaama thadukka
            word = re.sub(r'(.)\1+', r'\1', word) # Double letters ah single aakura (masterr -> master)
            word = re.sub(r'[aeiouAEIOU]', '.', word) # Vowels ah dot aakura (mester -> m.st.r)
            fuzzy_keywords.append(word)
            
        fuzzy_pattern = "".join([f"(?=.*{word})" for word in fuzzy_keywords])
        try:
            regex = re.compile(fuzzy_pattern, flags=re.IGNORECASE)
            filter_db = {'$or': [{'file_name': regex}, {'caption': regex}]}
            if file_type: filter_db['file_type'] = file_type
            total_results = await Media.count_documents(filter_db)
        except:
            pass

    # LEVEL 3: YEAR IGNORE SEARCH (For 'Master 2022' when DB has 'Master')
    if total_results == 0:
        no_num_query = re.sub(r'\b\d{4}\b', '', clean_query).strip() # 4 digit years ah remove pandrom
        no_num_keywords = no_num_query.split()
        if no_num_keywords and no_num_keywords != keywords:
            fn_keywords = []
            for word in no_num_keywords:
                word = re.escape(word)
                word = re.sub(r'(.)\1+', r'\1', word)
                word = re.sub(r'[aeiouAEIOU]', '.', word)
                fn_keywords.append(word)
                
            raw_pattern_2 = "".join([f"(?=.*{word})" for word in fn_keywords])
            try:
                regex = re.compile(raw_pattern_2, flags=re.IGNORECASE)
                filter_db = {'$or': [{'file_name': regex}, {'caption': regex}]}
                if file_type: filter_db['file_type'] = file_type
                total_results = await Media.count_documents(filter_db)
            except:
                pass

    next_offset = offset + max_results
    if next_offset >= total_results:
        next_offset = ''

    cursor = Media.find(filter_db)
    # File size (Low MB to High GB) vachu database-laye sort pandrom
    cursor.sort('file_size', 1)
    cursor.skip(offset).limit(max_results)
    files = await cursor.to_list(length=max_results)

    return files, next_offset, total_results

async def get_file_details(query):
    filter = {'$or': [{'file_id': query}, {'_id': query}]}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    if not filedetails:
        filedetails = await Media.collection.find({'_id': query}).to_list(length=1)
    return filedetails

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref

async def get_movie_list(limit=20):
    cursor = Media.find().sort("$natural", -1).limit(100)
    files = await cursor.to_list(length=100)
    results = []
    for file in files:
        name = getattr(file, "file_name", "")
        if not re.search(r"(s\d{1,2}|season\s*\d+).*?(e\d{1,2}|episode\s*\d+)", name, re.I):
            results.append(name)
        if len(results) >= limit:
            break
    return results

async def get_series_grouped(limit=30):
    cursor = Media.find().sort("$natural", -1).limit(150)
    files = await cursor.to_list(length=150)
    grouped = defaultdict(list)
    for file in files:
        name = getattr(file, "file_name", "")
        match = re.search(r"(.*?)(?:S\d{1,2}|Season\s*\d+).*?(?:E|Ep|Episode)?(\d{1,2})", name, re.I)
        if match:
            title = match.group(1).strip().title()
            episode = int(match.group(2))
            grouped[title].append(episode)

    return {
        title: sorted(set(eps))[:10]
        for title, eps in grouped.items() if eps
    }
