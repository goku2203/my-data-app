<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=240&color=0:0f2027,50:203a43,100:2c5364&text=Mikasa%20Filter%20Bot&fontSize=64&fontColor=ffffff&fontAlign=50&fontAlignY=40&animation=fadeIn&desc=Index%20%E2%80%A2%20Search%20%E2%80%A2%20Verify%20%E2%80%A2%20Autopost&descSize=22&descAlign=50&descAlignY=64" alt="Mikasa Filter Bot" width="100%" />

<p>
  A fast Telegram bot for <b>file indexing, smart search, verification and channel automation</b>.<br/>
  Built with Pyrofork + MongoDB, deployed on Render.
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Pyrofork-2.3-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Pyrofork" />
  <img src="https://img.shields.io/badge/MongoDB-Database-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
  <img src="https://img.shields.io/badge/Render-Deploy-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

<p>
  <a href="#-features">Features</a> •
  <a href="#-whats-new">What's New</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-environment-variables">Variables</a> •
  <a href="#-deployment">Deploy</a> •
  <a href="#-commands">Commands</a>
</p>

</div>

---

## ✨ Features

| | |
|---|---|
| 🔎 **Smart Search** | Auto filter in groups and PM, with spell-check suggestions |
| 🗂️ **File Indexing** | Save files from your database channels straight into MongoDB |
| ✅ **Verification** | Web verify page (`/verify`) + shortlink. The pending file is delivered right after verifying |
| 🤖 **Autopost** | Groups files by title, detects year / audio / quality / size, adds a TMDB poster and posts to your updates channel |
| 🔔 **New File Alerts** | Clean "added" alerts in your alert channel with a duplicate guard |
| 📢 **Force Subscribe** | Multiple channels, with join-request support |
| 📊 **Live Status** | `/stats` dashboard: uptime, users, groups, files, DB usage, CPU and RAM |
| 🗑️ **Auto Delete** | Sent files are removed after a set time |
| 💎 **Premium Menu** | Plans and payment flow inside the bot |
| 🔁 **Always Online** | Built-in web server, keep-alive ping and a midnight (IST) auto restart |

---

## 🆕 What's New

- 🐛 **Verify fix** – after verification the user gets their file instead of *File Not Found*
- 🌐 **Web server** – `/` and `/health` for Render, `/verify` for the verification page
- 🛠️ **`/vsettings`** – change verify mode and duration from inside Telegram
- 🤖 **Autopost** – `/autopost` ON/OFF with batched posts and TMDB posters
- 🔔 **New file alerts** – separate channels for movies, anime, requests and cam prints
- 📊 **New `/stats` dashboard** – refresh button, auto-closes after 10 minutes
- 🧹 **`/cleandb` and `/scanmovie`** – remove cam prints, check HD vs cam files
- 🔁 **Midnight restart** – restarts at 12:00 AM IST and cleans up the log message
- 🎨 **README** – redesigned

---

## 📁 Project Structure

```text
my-data-app/
├── bot.py              # Entry point + web server + keep-alive
├── info.py             # All settings (environment variables)
├── Script.py           # Bot texts
├── utils.py            # Helpers
├── verify.html         # Verification page
├── database/           # MongoDB layers
│   ├── ia_filterdb.py      # Files + search
│   ├── users_chats_db.py   # Users, chats, bans, settings
│   ├── channel_db.py       # Index channels
│   └── connections_mdb.py  # Group connections
├── plugins/            # Bot features
│   ├── commands.py         # /start, file delivery, verify flow
│   ├── pm_filter.py        # Auto filter
│   ├── autopost.py         # Autopost to updates channel
│   ├── new_alert.py        # New file alerts
│   ├── db_listener.py      # Live saving of new files
│   ├── index.py            # Channel indexing
│   ├── status.py           # /stats dashboard
│   ├── admin_commands.py   # /admin, /vstats, /vsettings
│   ├── group_manager.py    # Groups, ban / unban, users
│   ├── fsub_manager.py     # Force subscribe
│   ├── join_request.py     # Join request tracking
│   ├── deletefiles.py      # Delete / scan files
│   ├── db_cleaner.py       # Cam print cleaner
│   ├── movies_series.py    # /movies, /series
│   ├── premium.py          # Premium plans
│   └── ...                 # menu, welcome, broadcast, etc.
├── Dockerfile
├── render.yaml
├── requirements.txt
└── runtime.txt
```

---

## 🔧 Environment Variables

Set these in Render → *Environment* or a local `.env` file. Never commit real keys.

### Required

| Variable | Description |
|---|---|
| `API_ID`, `API_HASH` | From [my.telegram.org](https://my.telegram.org/apps) |
| `BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) |
| `DATABASE_URI` | MongoDB connection string |
| `ADMINS` | Admin user IDs (space-separated) |
| `CHANNELS` | Channel IDs to index (space-separated) |
| `LOG_CHANNEL` | Channel for bot logs |

### Optional

| Variable | Description |
|---|---|
| `AUTH_CHANNEL` | Force-subscribe channel IDs |
| `IS_VERIFY`, `VERIFY_EXPIRE`, `VERIFY_LOG_CHANNEL` | Verification system |
| `SHORTLINK_URL`, `SHORTLINK_API` | Shortlink provider |
| `TMDB_API_KEY` | Posters for autopost |
| `UPDATES_CHANNEL` | Where autopost publishes |
| `MOVIE_DB_CHANNEL`, `ANIME_CHANNEL_ID`, `USER_REQ_DB_CHANNEL`, `CAM_DB_CHANNEL` | Source channels |
| `ALERT_LOG_CHANNEL_ID`, `MISSING_LOG_CHANNEL` | Alert and missing logs |
| `FILE_AUTO_DELETE_SECONDS` | Delay before sent files are deleted |
| `RENDER_URL` | Your Render URL, used for keep-alive |
| `PORT` | Set automatically by Render |

Full list with defaults: [`info.py`](info.py)

---

## 🚀 Deployment

### ☁️ Render (recommended)

1. Fork or clone this repo.
2. On [Render](https://render.com) create a **New Web Service** from the repo (a `render.yaml` blueprint is included).
3. Runtime: **Docker**. Health check path: `/health`.
4. Add the environment variables.
5. Deploy 🎉

### 🐳 Docker

```bash
git clone https://github.com/goku2203/my-data-app
cd my-data-app
docker build -t my-data-app .
docker run -d --env-file .env my-data-app
```

### 🖥️ VPS / Local

```bash
git clone https://github.com/goku2203/my-data-app
cd my-data-app
pip3 install -U -r requirements.txt
python3 bot.py
```

> Requires **Python 3.10**.

---

## 💬 Commands

### 👤 Users

| Command | Description |
|---|---|
| `/start` | Start the bot |
| `/movies`, `/series` | Recently added items |
| `/plan` | Premium plans |

### 👑 Admins

| Command | Description |
|---|---|
| `/admin` | Admin command menu |
| `/stats`, `/status` | Live status dashboard |
| `/autopost` | Turn autopost ON / OFF |
| `/vsettings`, `/vstats` | Verify settings and stats |
| `/settings` | Auto-filter settings |
| `/deletefiles`, `/cleandb`, `/scanmovie` | File management |
| `/addfsub`, `/delfsub`, `/listfsub` | Force-subscribe channels |
| `/broadcast` | Message all users |
| `/ban`, `/unban`, `/enable`, `/disable`, `/leave` | User and chat control |
| `/ping`, `/usage`, `/restart` | System tools |

---

## ⚖️ License & Disclaimer

Released under the [LICENSE](LICENSE). Built on open-source Telegram bot work and [Pyrofork](https://github.com/Mayuri-Chan/pyrofork).

You are responsible for the content you index, store or share. Use only files you have the right to distribute and follow Telegram's Terms of Service.

---

<div align="center">

### 💜 Made by **Goku Stark**

<a href="https://github.com/goku2203">
  <img src="https://img.shields.io/badge/GitHub-goku2203-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
</a>

⭐ If this project helped you, drop a star!

<img src="https://capsule-render.vercel.app/api?type=waving&height=100&color=0:0f2027,50:203a43,100:2c5364&section=footer" alt="footer" width="100%" />

</div>
