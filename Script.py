class script(object):

    # ==========================================
    # 🟢 MAIN BOT COMMANDS TEXTS
    # ==========================================

    START_TXT = """<b>👋 Hello {}!</b>

<b>🤖 I am Mikasa, your file search assistant.</b>

<i>I can help you find Movies, Series, and Anime files quickly in your group. ⚡</i>

<b>How to use me:</b>

1. Add me to your group.
2. Make me an <b>Admin</b>.
3. Search and enjoy unlimited files! 🎬

<blockquote>❤️ I am always here to help you.</blockquote>

<i>Click the buttons below to learn more.</i>"""


    HELP_TXT = """<blockquote><b>⚙️ Help & System Status</b></blockquote>

<b>👤 User:</b> {}
<b>📡 Server:</b> Free Tier (Experimental) ⚠️

<i>I am currently running on a free server, so I might be a little slow. Please be patient! 🐢</i>

<b>🚫 Important:</b>
Please <b>Don't Spam</b> commands, or I might crash (die) 😵.

<b>👇 Choose a category below:</b>"""

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

<blockquote><b><i>❤️ I’ll always be here when you need me.</i></b></blockquote>"""


    SOURCE_TXT = """<blockquote><b>🛠️ Source Code</b></blockquote>

<i>This project is Open Source. You can find the code below.</i>

<b>👨‍💻 Developer:</b> <a href="https://t.me/Goku_Stark">Goku Stark</a>
<b>📂 Repository:</b> <a href="https://t.me/Goku_Stark">Click Here</a>"""

    # ==========================================
    # 🔵 GUIDES & TUTORIAL TEXTS
    # ==========================================

    MANUALFILTER_TXT = """<blockquote><b>🛠️ Manual Filters Help</b></blockquote>

<i>Filters allow the bot to reply automatically when a specific keyword is detected.</i>

<b>📝 Rules:</b>
1. Bot must be an <b>Admin</b>.
2. Only Admins can set filters.
3. Buttons have a 64-character limit.

<b>🎮 Commands:</b>
• /filter - <code>Add a new filter</code>
• /filters - <code>List all active filters</code>
• /del - <code>Delete a specific filter</code>
• /delall - <code>Delete all filters (Owner only)</code>"""

    BUTTON_TXT = """<blockquote><b>🔘 Button Formatting Help</b></blockquote>

<i>I support both URL and Alert (Pop-up) buttons.</i>

<b>⚠️ Note:</b> Buttons must have content (text/media).

<b>1️⃣ URL Button Format:</b>
<code>[Button Text](buttonurl:https://t.me/Goku_Stark)</code>

<b>2️⃣ Alert Button Format:</b>
<code>[Button Text](buttonalert:This is a pop-up message!)</code>"""

    AUTOFILTER_TXT = """<blockquote><b>🤖 Auto-Filter Guide</b></blockquote>

<b>1️⃣ For Private Channels:</b>
• Make me an <b>Admin</b> in your channel.
• Ensure the channel has <b>NO</b> porn/fake files.
• Forward the last message from your channel to me (with quotes).
• I will index all files automatically! 📂

<b>2️⃣ For Groups:</b>
• Add me as an <b>Admin</b>.
• Use <code>/connect</code> to link your group to my PM.
• Use <code>/settings</code> in PM to enable Auto-Filter.
"""

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

    LOG_TEXT_P = """<b>✨ ɴᴇᴡ ᴜsᴇʀ ✨</b>

👤 <b>ᴜsᴇʀ :</b> {0}
🆔 <b>ᴜsᴇʀ ɪᴅ :</b> <code>{1}</code>"""


    MISSING_LOG_TXT = """<b>⚠️ 𝐅𝐢𝐥𝐞 𝐌𝐢𝐬𝐬𝐢𝐧𝐠</b>

📁 <b>ꜰɪʟᴇ :</b> <code>{2}</code>
|
├ 👤 <b>ᴜsᴇʀ :</b> {0}
├ 🆔 <b>ᴜsᴇʀ ɪᴅ :</b> <code>{1}</code>
└ 🌐 <b>sᴏᴜʀᴄᴇ :</b> {3}"""

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
    
    DELETED_FILE_TXT = """<b>  File Not Found! (Deleted)</b>\n
<blockquote><b>Eng:</b><i>Sorry! This file was deleted because the HD version is available. Please search the channel or bot to get the HD file.
</i></blockquote>\n<blockquote><b>Tan:</b><i>Sorry! HD version vanthathunala intha file delete panniyachu. HD file-ku channel or bot-la search pannunga.</i>"""

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
    
🔍 <b>Eng:</b> I couldn’t find your movie  
🔍 <b>Tanglish:</b> Nee thedina movie kidaikala bro

⚠️ <b>Reason irukkalam:</b>  
<blockquote>• 🔤 Spelling konjam wrong ah irukkalam  
• 📂 My Database la file illa</blockquote>

✨ <b>Quick Fix:</b>  
<blockquote>• ✅ Correct ah type pannunga  
• 🎯 Movie name mattum podunga  
• 🚫 Release aagala movie avoid pannunga</blockquote>

🌐 <b>Still miss aagudha?</b>  
👉 <b>Google la search pannunga bro 👇</b>"""

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

    OLD_MES = """<b>⚠️ Request Expired!</b>
    
<i>You are clicking an old message. Please request the file again.</i> 🔄"""

    MOV_NT_FND = """<b>❌ Movie Not Found!</b>

<i>This movie is not yet released or not added to my database.</i>

<pre>Use /bugs to request this movie.</pre>"""

    RESTART_TXT = """<b>✅ Bot Restarted Successfully!</b>"""
    
    RESTART_GC_TXT = """<b>♻️ System Restarted!</b>

<b>📅 Date:</b> <code>{}</code>
<b>⏰ Time:</b> <code>{}</code>
<b>🌐 Zone:</b> <code>Asia/Kolkata</code>
<b>🛠️ Version:</b> <code>v2.0 [Stable]</code>"""
