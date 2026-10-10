<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=250&color=0:0f2027,50:203a43,100:2c5364&text=Goku%20Stark&fontSize=80&fontColor=ffffff&fontAlign=50&fontAlignY=38&animation=fadeIn&desc=Mikasa%20Filter%20Bot&descSize=26&descAlign=50&descAlignY=62" alt="Goku Stark" width="100%" />

<a href="https://github.com/goku2203/my-data-app">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=24&duration=3200&pause=900&color=38BDF8&center=true&vCenter=true&width=640&height=48&lines=Hi%2C+I%27m+Goku+Stark+%F0%9F%91%8B;Mikasa+Filter+Bot+%F0%9F%A4%96;Fast+%E2%80%A2+Smart+%E2%80%A2+Automated" alt="Typing animation" />
</a>

<p>
  A powerful Telegram bot for <b>file indexing, smart search, auto filtering, verification and channel automation</b> — deployed on Render with MongoDB.
</p>

<p>
  <a href="https://github.com/goku2203/my-data-app/stargazers">
    <img src="https://img.shields.io/github/stars/goku2203/my-data-app?style=for-the-badge&logo=github&color=fbbf24&logoColor=white" alt="Stars" />
  </a>
  <a href="https://github.com/goku2203/my-data-app/network/members">
    <img src="https://img.shields.io/github/forks/goku2203/my-data-app?style=for-the-badge&logo=github&color=38bdf8&logoColor=white" alt="Forks" />
  </a>
  <a href="https://github.com/goku2203/my-data-app/commits/main">
    <img src="https://img.shields.io/github/last-commit/goku2203/my-data-app?style=for-the-badge&logo=github&color=a78bfa&logoColor=white" alt="Last Commit" />
  </a>
  <a href="https://github.com/goku2203/my-data-app">
    <img src="https://img.shields.io/github/repo-size/goku2203/my-data-app?style=for-the-badge&logo=github&color=f472b6&logoColor=white" alt="Repo Size" />
  </a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10" />
  <img src="https://img.shields.io/pypi/v/pyrofork?style=for-the-badge&logo=telegram&logoColor=white&label=pyrofork&color=26A5E4" alt="Pyrofork" />
  <img src="https://img.shields.io/badge/MongoDB-Database-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
  <img src="https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

<p>
  <a href="#-features">Features</a> •
  <a href="#️-whats-customized">Customizations</a> •
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
| 🔎 **Smart Search** | Auto filter in groups, manual filters, inline search, spell-check suggestions |
| 🗂️ **File Indexing** | Index files from channels, store them in MongoDB, add or remove index channels on the fly |
| 🤖 **Autopost** | Groups files of the same title, detects year / audio / quality / size, fetches a TMDB image and posts a clean caption with size-wise links to your updates channel |
| 🔔 **New File Alerts** | Sends an alert to your alert channel whenever new files land in your database channels |
| ✅ **Verification System** | Web verify page (`/verify`) + shortlink support, with the pending file delivered right after verification |
| 👑 **Owner Control Panel** | Live stats: uptime, ping, users, groups, files, monthly verified, MongoDB usage, CPU and RAM |
| 📢 **Force Subscribe** | Multiple request-FSub channels, managed with `/fsub` |
| 🗑️ **Auto Delete** | Files sent to users are removed automatically after a set time |
| 📣 **Broadcast** | Message all users and chats from one command |
| 🚫 **Ban / Unban** | Block users or chats, enable or disable chats |
| 🔁 **Keep Alive** | Built-in web server and self-ping so free hosting does not put the bot to sleep |
| 🚀 **Auto Update** | GitHub Action triggers a fresh Render deploy every day |

---

## 🛠️ What's Customized

A summary of what has been added or changed in this project, file by file.

### Core

| File | What it does / what changed |
|---|---|
| `bot.py` | Entry point. Starts the Pyrofork client **and** an aiohttp web server (`/` health route, `/verify` verification page). Keep-alive ping loop, IST restart message to the log channel, loads maintenance mode and banned users on start |
| `info.py` | All settings read from environment variables. Extended with Render URL, keep-alive URL, verification + shortlink options, TMDB key, and separate channels for updates, anime, user requests, alerts, missing logs and database storage |
| `Script.py` | Bot texts and message templates |
| `utils.py` | Shared helpers (file size formatting, force-sub checks, shortlinks, temp state) |
| `verify.html` | Verification landing page served by the bot at `/verify?code=...` |
| `logging.conf` | Logging setup |

### Plugins (`plugins/`)

| File | What it does / what changed |
|---|---|
| `commands.py` | `/start`, file delivery and the verify flow. **Fixed:** after verifying, the user's pending file is now delivered instead of showing *File Not Found* |
| `control_panel.py` | **New:** owner panel (`/stats`, `/panel`) with live system + database stats and a *Manage Index Channels* menu (`/addchannel`, `/delchannel`) |
| `autopost.py` | **New:** `/autopost` ON/OFF toggle. Batches files of one title, builds a formatted caption (year, audio, quality, size links) and posts it with a TMDB image to the updates channel |
| `new_alert.py` | **New:** posts clean "added" alerts to the alert channel, with a 5-minute duplicate guard per title |
| `index.py`, `channel.py`, `manage_channels.py` | Channel indexing and live saving of new files into the database |
| `pm_filter.py`, `filters.py` | Auto filter results and manual filters |
| `inline.py` | Inline search |
| `fsub_manager.py` | Multiple force-subscribe channels |
| `deletefiles.py` | Delete files from the database by keyword |
| `db_cleaner.py` | Database cleanup tools |
| `movies_series.py` | `/movies` and `/series` latest-added lists |
| `premium.py` | Premium user handling |
| `broadcast.py`, `banned.py`, `admin_commands.py` | Broadcast, ban / unban and other admin tools |
| `welcome.py`, `setphoto.py`, `menu.py`, `settings_cb.py`, `etc.py`, `p_ttishow.py`, `connection.py`, `bots.py` | Welcome messages, start photos, menus, group settings, utility commands and connections |

### Database (`database/`)

| File | Purpose |
|---|---|
| `ia_filterdb.py` | Indexed files storage and search |
| `users_chats_db.py` | Users, chats, bans, settings, verification status, autopost + maintenance flags |
| `channel_db.py` | **New:** index channels stored in the database (add / remove without redeploying) |
| `filters_mdb.py` | Manual filters |
| `connections_mdb.py` | Group connections |

### Deployment files

| File | Purpose |
|---|---|
| `Dockerfile` | `python:3.10` image, installs requirements and runs `bot.py` |
| `Procfile` | `web: python3 bot.py` for worker/web platforms |
| `runtime.txt` | Python version (`python-3.10.10`) |
| `app.json` | One-click deploy manifest |
| `requirements.txt` | Python dependencies |
| `.github/workflows/update.yml` | **Render Auto Update** — runs daily at 18:30 UTC (00:00 IST) and calls your Render deploy hook |

### 📝 Changelog

- 🎨 README redesigned: animated name banner, new badges, file-by-file guide, variables table and deployment steps
- 🐛 Verify flow fixed: pending file is delivered after verification (`plugins/commands.py`)
- 👑 Owner control panel and dynamic index channel management added
- 🤖 Smart autopost with TMDB images added
- 🔔 New-file alert system added
- 🌐 Built-in web server with `/verify` page and keep-alive added
- ☁️ Render auto-update workflow added

---

## 📁 Project Structure

```text
my-data-app/
├── .github/workflows/update.yml   # Daily Render deploy trigger
├── database/                      # MongoDB layers
│   ├── channel_db.py
│   ├── connections_mdb.py
│   ├── filters_mdb.py
│   ├── ia_filterdb.py
│   └── users_chats_db.py
├── plugins/                       # All bot features
├── Dockerfile
├── Procfile
├── Script.py
├── app.json
├── bot.py                         # Entry point + web server
├── info.py                        # Config / environment variables
├── logging.conf
├── requirements.txt
├── runtime.txt
├── utils.py
└── verify.html                    # Verification page
```

---

## 🔧 Environment Variables

Set these in your hosting dashboard (Render → *Environment*) or in a local `.env` file. Never commit real tokens or keys to GitHub.

### Required

| Variable | Description |
|---|---|
| `API_ID` | From [my.telegram.org](https://my.telegram.org/apps) |
| `API_HASH` | From [my.telegram.org](https://my.telegram.org/apps) |
| `BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) |
| `DATABASE_URI` | MongoDB connection string |
| `ADMINS` | Admin user IDs or usernames (space-separated) |
| `CHANNELS` | Channel / group IDs to index (space-separated) |
| `LOG_CHANNEL` | Channel ID for bot logs |

### Optional

| Variable | Description |
|---|---|
| `BOT_USERNAME` | Bot username |
| `DATABASE_NAME`, `COLLECTION_NAME` | MongoDB database and collection names |
| `PICS` | Image links for the start message (space-separated) |
| `AUTH_CHANNEL`, `REQUEST_FSUB_MODE` | Force-subscribe channels and request-FSub mode |
| `AUTH_USERS`, `AUTH_GROUPS` | Restrict usage to certain users or groups |
| `FILE_CHANNELS`, `FILE_CHANNEL_SENDING_MODE` | Channel file-sending mode |
| `FILE_AUTO_DELETE_SECONDS` | Delay before sent files are deleted |
| `IS_VERIFY`, `VERIFY_EXPIRE`, `VERIFY_LOG_CHANNEL` | Verification system |
| `SHORTLINK_URL`, `SHORTLINK_API` | Shortlink provider for verification |
| `TMDB_API_KEY` | Enables posters for autopost |
| `UPDATES_CHANNEL` | Where autopost publishes |
| `MOVIE_DB_CHANNEL`, `ANIME_CHANNEL_ID`, `USER_REQ_DB_CHANNEL`, `CAM_DB_CHANNEL` | Source channels used by alerts and autopost routing |
| `ALERT_LOG_CHANNEL_ID`, `MISSING_LOG_CHANNEL` | Alert and missing-request logs |
| `RENDER_URL`, `KEEP_ALIVE_URL` | Your deployed URL and keep-alive ping target |
| `HYPER_MODE`, `IMDB`, `SINGLE_BUTTON`, `SPELL_CHECK_REPLY`, `PROTECT_CONTENT` | UI and behaviour switches |
| `CUSTOM_FILE_CAPTION`, `BATCH_FILE_CAPTION`, `IMDB_TEMPLATE` | Caption and template overrides |
| `PORT` | Web server port (Render sets this automatically) |

See [`info.py`](info.py) for the full list and defaults.

---

## 🚀 Deployment

### ☁️ Render (Docker)

1. Fork or clone this repository.
2. On [Render](https://render.com), create a **New Web Service** and connect the repo.
3. Choose **Docker** as the runtime (the included `Dockerfile` is used).
4. Add the environment variables from the table above.
5. Deploy. The bot's web server answers on `/` so Render sees it as healthy.
6. *(Optional)* For daily auto-deploys, add your Render deploy hook URL as a repository secret named `RENDER_DEPLOY_HOOK`.

### 🐳 Docker

```bash
git clone https://github.com/goku2203/my-data-app
cd my-data-app
docker build -t my-data-app .
docker run -d --env-file .env --name my-data-app my-data-app
```

### 🖥️ VPS / Local

```bash
git clone https://github.com/goku2203/my-data-app
cd my-data-app
pip3 install -U -r requirements.txt
# set the environment variables (or create a .env file), then:
python3 bot.py
```

> Requires **Python 3.10**.

---

## 💬 Commands

### 👤 Users

| Command | Description |
|---|---|
| `/start` | Start the bot |
| `/movies`, `/series` | Show recently added items |

### 👑 Admins

| Command | Description |
|---|---|
| `/stats`, `/panel` | Open the owner control panel |
| `/autopost` | Turn autopost ON / OFF |
| `/addchannel <id>` | Add an index channel |
| `/delchannel <id>` | Remove an index channel |
| `/deletefiles <keyword>` | Delete database files whose name contains the keyword |
| `/fsub <ids>` | Update force-subscribe channels |
| `/broadcast` | Broadcast a message to all users |

---

## ⚖️ License & Disclaimer

This project is released under the license in the [LICENSE](LICENSE) file. It builds on open-source Telegram bot work and the [Pyrofork](https://github.com/Mayuri-Chan/pyrofork) library.

You are responsible for the content you index, store or share with this bot. Use it only with files you own or have the right to distribute, and follow Telegram's Terms of Service and the copyright laws of your country.

---

<div align="center">

### 💜 Made by **Goku Stark**

<a href="https://github.com/goku2203">
  <img src="https://img.shields.io/badge/GitHub-goku2203-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
</a>

⭐ If this project helped you, drop a star on the repo!

<img src="https://capsule-render.vercel.app/api?type=waving&height=120&color=0:0f2027,50:203a43,100:2c5364&section=footer" alt="footer" width="100%" />

</div>
