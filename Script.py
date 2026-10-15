class script(object):

    # ==========================================
    # 🟢 MAIN BOT COMMANDS TEXTS
    # ==========================================

    START_TXT = """<blockquote><b>⚡ Hᴇʏ {}!</b></blockquote>
    
<blockquote><b>🎌 Wᴇʟᴄᴏᴍᴇ ᴛᴏ Mɪᴋᴀsᴀ Bᴏᴛ!</b></blockquote>

<blockquote><i>🎬 Sᴇᴀʀᴄʜ ғᴏʀ Mᴏᴠɪᴇs, Aɴɪᴍᴇ, Sᴇʀɪᴇs🎬</i>
<i>⚡ Gᴇᴛ ғɪʟᴇs ɪɴ sᴇᴄᴏɴᴅs!</i></blockquote>

<blockquote><b>❤️ I Aᴍ Aʟᴡᴀʏs Hᴇʀᴇ Tᴏ Hᴇʟᴘ Yᴏᴜ...</b></blockquote>"""

    HELP_TXT = """<b>👋 Welcome to the Help Menu!</b>

<i>Here is how you can easily find and download your favorite files:</i>

<blockquote><b>🔍 How to Search:</b>
Just type the <b>Movie or Series name</b> directly in the chat or group. <i>Make sure to check the spelling on Google first!</i></blockquote>

<blockquote><b>⚡ Extra Features:</b>
• <b>Inline Search:</b> Type our bot username in any chat to search files quickly.
• <b>Premium Access:</b> Use /plan to check <i>fast download</i> and <i>ad-free</i> options.</blockquote>

<i>Still facing an issue? Contact the admin for support!</i>"""

    MAINT_TXT = (
        "<b>⚠️ Bot is Under Maintenance! 🛠️</b>\n\n<i>5 to 10 minutes wait pannunga. Work nadanthutu irukku!</i>"
    )

    ABOUT_TXT = """<blockquote><b>🤖 ʙᴏᴛ ᴘʀᴏꜰɪʟᴇ</b></blockquote>

╭─❖ <b>sʏsᴛᴇᴍ ɪɴꜰᴏ</b>
├ 👤 <b>ᴍʏ ɴᴀᴍᴇ:</b> ᴍɪᴋᴀꜱᴀ ᴀᴄᴋᴇʀᴍᴀɴ
├ 🤖 <b>ʙᴏᴛ :</b> {}
├ 👑 <b>ᴄʀᴇᴀᴛᴏʀ :</b> <a href="https://t.me/Goku_Stark">Goku Stark</a>
├ 💻 <b>ʟᴀɴɢᴜᴀɢᴇ :</b> Python 3
├ 💾 <b>ᴅᴀᴛᴀʙᴀsᴇ :</b> MongoDB
╰ ☁️ <b>sᴇʀᴠᴇʀ :</b> Koyeb

<blockquote><b><i>❤️ I’ʟʟ Aʟᴡᴀʏs Bᴇ Hᴇʀᴇ Wʜᴇɴ Yᴏᴜ Nᴇᴇᴅ Mᴇ...</i></b></blockquote>"""


    SOURCE_TXT = """<blockquote><b>🛠️ Source Code</b></blockquote>

<i>This project is Open Source. You can find the code below.</i>

<b>👨‍💻 Developer:</b> <a href="https://t.me/Goku_Stark">Goku Stark</a>
<b>📂 Repository:</b> <a href="https://t.me/Goku_Stark">Click Here</a>"""

    # ==========================================
    # 🔵 GUIDES & TUTORIAL TEXTS
    # ==========================================

    CONNECTION_TXT = """<blockquote><b>🔗 Connection Manager</b></blockquote>

<i>Connect your groups to my PM to manage filters easily and avoid spam.</i>

<b>🎮 Commands:</b>
• /connect - <code>Connect a group to PM</code>
• /disconnect - <code>Disconnect a group</code>
• /connections - <code>View active connections</code>"""

    # ==========================================
    # 🔴 ADMIN & SYSTEM LOG TEXTS
    # ==========================================
    LOG_TEXT_G = """<b>✨ ɴᴇᴡ ɢʀᴏᴜᴘ ᴄᴏɴɴᴇᴄᴛᴇᴅ</b>

╭─❖ <b>ɢʀᴏᴜᴘ ᴅᴇᴛᴀɪʟs</b>
├ 📌 <b>sᴛᴀᴛᴜs :</b> Active
├ 👥 <b>ɢʀᴏᴜᴘ :</b> {}
├ 🆔 <b>ɢʀᴏᴜᴘ ɪᴅ :</b> <code>{}</code>
├ 👤 <b>ᴍᴇᴍʙᴇʀs :</b> {}
╰ ➕ <b>ᴀᴅᴅᴇᴅ ʙʏ :</b> {}

<blockquote>⚙️ Waiting for admin setup...</blockquote>"""

    LOG_TEXT_P = """<b>✨ Nᴇᴡ Usᴇʀ</b>

<blockquote>👤 <b>Usᴇʀ :</b> {1}
🆔 <b>Usᴇʀ ID :</b> <code>{0}</code></blockquote>"""


    MISSING_LOG_TXT = """<b>Mɪssɪɴɢ Fɪʟᴇ</b>

<b>📁 Nᴀᴍᴇ ▼</b>

<blockquote><code>{2}</code></blockquote>

<blockquote>👤 <b>Usᴇʀ :</b> {0}
🆔 <b>Usᴇʀ ID :</b> <code>{1}</code>
🌐 <b>Sᴏᴜʀᴄᴇ :</b> {3}</blockquote>"""

    # ==========================================
    #   VERIFICATION LOG TEXT
    # ==========================================
    VERIFY_LOG_TXT = """<b>✅ Nᴇᴡ Usᴇʀ Vᴇʀɪғɪᴇᴅ!</b>\n
👤 <b>Usᴇʀ:</b> {mention}
🆔 <b>ɪᴅ:</b> <code>{id}</code>
⏳ <b>Mᴏᴅᴇ:</b> {mode}"""

# ==========================================
    # MISSING LOG - Number List
# ==========================================

# {0} = User Name
# {1} = User ID
# {2} = Query (Search)
# {3} = Source

    # ==========================================
    #   DELETED / MISSING FILE ALERT
    # ==========================================
    
    DELETED_FILE_TXT = """<b> 🗑️ File Not Found! (Deleted)</b>\n
<blockquote><b>Eng: </b><i>Sorry! This file was deleted because the HD version is available. Please search the channel or bot to get the HD file.
</i></blockquote>\n<blockquote><b>Tan: </b><i>Sorry! HD version vanthathunala intha file delete panniyachu. HD file-ku channel or bot-la search pannunga.</i></blockquote>"""

    # ==========================================
    # 🎬 MOVIE SEARCH & RESULTS TEXTS
    # ==========================================

    RESULT_TXT = (
    "<blockquote><b>⚡ Found something for you!</b></blockquote>\n"
    "[ ⌛ Only 1 minute left! Hurry! ]\n\n"
    "<i>Check the results below:</i>"
    )
    
    CUSTOM_FILE_CAPTION = """<b>📂 Filename:</b> <b><i>{file_caption}</i></b>\n
<b>💾 Size:</b> <b>{file_size}</b>\n
<blockquote><b>📢 Join Our Channels : 👇</b>\n
    <b>➠ <a href='https://t.me/+cuus3LKv3OwxYjJl'>Anime Single File</a></b>
    <b>➠ <a href='https://t.me/+LxPgPQsF7tExZmFl'>Naruto Channel</a></b>
    <b>➠ <a href='https://t.me/Anime_single'>Anime Lover's</a></b></blockquote>
━━━━━━━━━━━━━━━━━━
<b>⚠️ COPYRIGHT WARNING ⚠️</b>\n
<blockquote><i>This message will</i> <b>AUTO-DELETE</b> <i>in</i> <b>10 Minute</b> <i>to prevent copyright strikes! ⏳</i>\n
<b><i>Please forward or save this file immediately!</i></b></blockquote>"""

    SPOLL_NOT_FND = """<b>🎬 Movie Not Found! 😕</b>

🔍 <b>Eng:</b> I couldn't find your movie.
🔍 <b>Tan:</b> Nee thedina movie kidaikala bro.

💡 <b>Quick Fix / Try this:</b>
<blockquote>• 🔤 Check spelling / Spelling check pannunga.
• 🎯 Type movie name only / Name mattum type pannunga.
• 📂 Not in DB / Namma DB-la illama irukkalam.</blockquote>

🌐 <b>Still missing? Search on Google 👇</b>"""

    # ==========================================
    # 🔠 SPELLING CHECK & ALERT TEXTS
    # ==========================================

    ENG_SPELL = """<b>💡 Spelling Check (English)</b>
    
1️⃣ Use correct spelling.
2️⃣ Check if the movie is released on OTT.
3️⃣ Try: <code>Movie Name Year</code>"""

    MAL_SPELL = """<b>💡 അക്ഷരത്തെറ്റ് പരിശോധന (Malayalam)</b>
    
1️⃣ ശരിയായ സ്പെല്ലിംഗ് ഉപയോഗിക്കുക.
2️⃣ OTT-യിൽ റിലീസ് ചെയ്തിട്ടുണ്ടോ എന്ന് പരിശോധിക്കുക.
3️⃣ ശ്രമിക്കുക: <code>Movie Name Year</code>"""

    HIN_SPELL = """<b>💡 वर्तनी जाँच (Hindi)</b>
    
1️⃣ सही वर्तनी का प्रयोग करें।
2️⃣ जांचें कि क्या फिल्म ओटीटी पर रिलीज हुई है।
3️⃣ प्रयास करें: <code>Movie Name Year</code>"""

    TAM_SPELL = """<b>💡 எழுத்துப்பிழை சரிபார்ப்பு (Tamil)</b>
    
1️⃣ சரியான எழுத்துப்பிழையை பயன்படுத்தவும்.
2️⃣ படம் OTT இல் வெளியாகிவிட்டதா என சரிபார்க்கவும்.
3️⃣ முயற்சிக்கவும்: <code>Movie Name Year</code>"""

    # ==========================================
    # 🔄 SYSTEM ALERTS & NOTIFICATIONS
    # ==========================================

    CHK_MOV_ALRT = """<b>♻️ Checking Database... Please Wait! ♻️</b>"""

    OLD_MES = """<b>  Request Expired!</b>
     <i>You are clicking an old message. Please request the file again.</i>"""
    
    MOV_NT_FND = """<b>  Movie Not Found!</b>

<i>This movie is not yet released or not added to my database.</i>

<pre>Use /bugs to request this movie.</pre>"""

    RESTART_TXT = """<b>✅ Bot Restarted Successfully!</b>"""
    
    RESTART_GC_TXT = """<b>♻️ System Restarted!</b>

<b>📅 Date:</b> <code>{}</code>
<b>⏰ Time:</b> <code>{}</code>
<b>🌐 Zone:</b> <code>Asia/Kolkata</code>
<b>🛠️ Version:</b> <code>v2.0 [Stable]</code>"""
