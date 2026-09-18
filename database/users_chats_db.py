import motor.motor_asyncio
import datetime
from info import DATABASE_NAME, DATABASE_URI, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.config = self.db.config

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )
        
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
        
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
        
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
        
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
        
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
        
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
        
    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)
        
    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return False if not chat else chat.get('chat_status')
        
    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
            
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
            
    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'template': IMDB_TEMPLATE
        }
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', default)
        return default
        
    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
        
    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
        
    async def get_all_chats(self):
        return self.grp.find({})

    async def set_auth_channels(self, channels: list[int]):
        # Store the list of auth channel IDs in a singleton document
        await self.config.update_one(
            {"_id": "auth_channels"},
            {"$set": {"channels": channels}},
            upsert=True,
        )

    async def get_auth_channels(self) -> list[int]:
        doc = await self.config.find_one({"_id": "auth_channels"})
        if doc and "channels" in doc:
            return doc["channels"]
        return []

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']

    # ==========================================
    #   SMART COUNTER CODE ADDED HERE (FIXED SPACES)
    # ==========================================
    async def add_verified_user(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        current_month = datetime.datetime.now().strftime("%Y-%m")
        await self.config.update_one(
            {"_id": "smart_counter"},
            {
                "$inc": {
                    f"daily_{today}": 1,
                    f"verified_{current_month}": 1,
                    "total_verified": 1
                }
            },
            upsert=True
        )

    async def get_verified_count(self):
        current_month = datetime.datetime.now().strftime("%Y-%m")
        stats = await self.config.find_one({"_id": "smart_counter"})
        if stats:
            return stats.get(f"verified_{current_month}", 0)
        return 0

    async def get_all_verify_stats(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        current_month = datetime.datetime.now().strftime("%Y-%m")
        stats = await self.config.find_one({"_id": "smart_counter"}) or {}
        
        daily = stats.get(f"daily_{today}", 0)
        monthly = stats.get(f"verified_{current_month}", 0)
        total = stats.get("total_verified", 0)
        
        # Right now active verified users (10 mins limit kulla irukkavanga)
        now = datetime.datetime.now()
        active_now = await self.col.count_documents({"verify_status_v2.verify_until": {"$gte": now}})
        
        return daily, monthly, total, active_now

    # ==========================================
    #   MAINTENANCE DB FUNCTIONS
    # ==========================================
    async def set_maintenance(self, status: bool):
        await self.col.update_one({'id': 'bot_settings'}, {'$set': {'maintenance': status}}, upsert=True)

    async def get_maintenance(self):
        config = await self.col.find_one({'id': 'bot_settings'})
        if config:
            return config.get('maintenance', False)
        return False

    # ==========================================
    #   AUTOPOST DB FUNCTIONS (PUTHUSA ADD PANNATHU)
    # ==========================================
    async def set_autopost(self, status: bool):
        await self.col.update_one({'id': 'bot_settings'}, {'$set': {'autopost': status}}, upsert=True)

    async def get_autopost(self):
        config = await self.col.find_one({'id': 'bot_settings'})
        if config:
            return config.get('autopost', True) # By default True
        return True

# ==========================================
    #   VERIFY & AUTO-DELETE SETTINGS 
    # ==========================================
    async def get_verify_settings(self):
        config = await self.col.find_one({'id': 'bot_settings'})
        if config and 'verify' in config:
            return config['verify']
        return {'mode': 'time', 'hours': 4}

    async def set_verify_settings(self, mode, hours):
        await self.col.update_one({'id': 'bot_settings'}, {'$set': {'verify': {'mode': mode, 'hours': hours}}}, upsert=True)

    async def get_autodelete_settings(self):
        config = await self.col.find_one({'id': 'bot_settings'})
        if config and 'autodelete' in config:
            return config['autodelete']
        return {'enabled': False, 'time': 5}

    async def set_autodelete_settings(self, enabled, time_mins):
        await self.col.update_one({'id': 'bot_settings'}, {'$set': {'autodelete': {'enabled': enabled, 'time': time_mins}}}, upsert=True)


# ==========================================
# Ithu file kadeisila thaan varanum
db = Database(DATABASE_URI, DATABASE_NAME)
