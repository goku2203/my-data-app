from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI, DATABASE_NAME

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
channel_col = db['auto_index_channels']

async def add_index_channel(chat_id):
    # Database la channel id add pandrathu
    if not await channel_col.find_one({'chat_id': int(chat_id)}):
        await channel_col.insert_one({'chat_id': int(chat_id)})

async def del_index_channel(chat_id):
    # Database la irunthu channel id remove pandrathu
    await channel_col.delete_one({'chat_id': int(chat_id)})

async def get_all_index_channels():
    # Database la irukkura ella channel ids-um edukkurathu
    channels = await channel_col.find({}).to_list(length=None)
    return [doc['chat_id'] for doc in channels]
