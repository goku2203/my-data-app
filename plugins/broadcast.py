from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages
import asyncio

BROADCAST_BATCH_SIZE = 20  # Safe limit for Telegram
BROADCAST_SLEEP = 3  # Increased delay to prevent flood waits

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text("Broadcasting your messages...")
    
    start_time = time.time()
    total_users = await db.total_users_count()
    done, blocked, deleted, failed, success = 0, 0, 0, 0, 0
    
    async def send_message(user):
        nonlocal success, blocked, deleted, failed
        user_id = int(user['id'])
        pti, sh = await broadcast_messages(user_id, b_msg)
        if pti:
            success += 1
        else:
            if sh == "Blocked":
                blocked += 1
                await db.delete_user(user_id)
            elif sh == "Deleted":
                deleted += 1
                await db.delete_user(user_id)
            elif sh == "Error":
                failed += 1

    tasks = []
    async for user in users:
        tasks.append(send_message(user))
        done += 1
        
        if len(tasks) >= BROADCAST_BATCH_SIZE:
            await asyncio.gather(*tasks)
            tasks = []
            # Update status message safely
            try:
                await sts.edit(
                    f"Broadcast in progress:\n\nTotal Users: {total_users}\nCompleted: {done} / {total_users}\n"
                    f"Success: {success} | Blocked: {blocked} | Deleted: {deleted} | Failed: {failed}"
                )
            except:
                pass
            await asyncio.sleep(BROADCAST_SLEEP)
            
    if tasks:
        await asyncio.gather(*tasks)
        
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(
        f"Broadcast Completed in {time_taken}.\n\nTotal Users: {total_users}\n"
        f"Success: {success} | Blocked: {blocked} | Deleted: {deleted} | Failed: {failed}"
    )
