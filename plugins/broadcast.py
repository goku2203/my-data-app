import asyncio
import datetime
import time
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast(bot, message):
    # 1. Ask for the message first
    ask_msg = await message.reply_text(
        "<b>Broadcast Message:</b>\n\nEnna message send pannanumo atha ippo type panni send pannunga.\n\nCancel panna <code>/cancel</code> nu type pannunga."
    )
    
    try:
        # Wait for user to send the message (Timeout after 5 minutes)
        b_msg = await bot.listen(message.chat.id, timeout=300)
    except asyncio.TimeoutError:
        return await ask_msg.edit("Time out aagiduchu! Thirumbavum /broadcast command use pannunga.")
        
    if b_msg.text and b_msg.text.startswith("/cancel"):
        return await ask_msg.edit("Broadcast cancel aagiduchu.")
        
    sts = await message.reply_text("Broadcasting your messages... Please wait.")
    
    start_time = time.time()
    total_users = await db.total_users_count()
    done, blocked, deleted, failed, success = 0, 0, 0, 0, 0
    
    users = await db.get_all_users()
    
    # 2. Sequential Processing
    async for user in users:
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
                
        done += 1
        
        # Update status message every 20 users safely
        if done % 20 == 0:
            try:
                await sts.edit(
                    f"Broadcast in progress:\n\nTotal Users: {total_users}\nCompleted: {done} / {total_users}\n"
                    f"Success: {success} | Blocked: {blocked} | Deleted: {deleted} | Failed: {failed}"
                )
            except:
                pass
            await asyncio.sleep(1) # Prevent FloodWait for status edit
            
        await asyncio.sleep(0.1) # Safe delay between each user to prevent Telegram blocks
        
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(
        f"Broadcast Completed in {time_taken}.\n\nTotal Users: {total_users}\n"
        f"Success: {success} | Blocked: {blocked} | Deleted: {deleted} | Failed: {failed}\n\n"
        f"<i>  Note: Intha message matrum command 1 minute-la auto-delete aagidum...</i>"
    )
    
    # 3. Auto-Delete Section (Safe Cleanup)
    await asyncio.sleep(60) # Wait for 1 minute before deleting
    try:
        await message.delete()  # Deletes /broadcast command
        await ask_msg.delete()  # Deletes Bot's question
        await b_msg.delete()    # Deletes your broadcast message
        await sts.delete()      # Deletes the final status report
    except:
        pass
