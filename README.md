<h1 align="center">🎵 <b>ᴀʏᴜsʜ ᴍᴜsɪᴄ ʙᴏᴛ</b> 🎵</h1>

<p align="center">
  <img src="https://telegra.ph/file/0c9a721757db6130d249d.jpg" width="400" style="border-radius: 15px;"/>
</p>

<p align="center">
  <b>⚡ An ultra-fast, feature-rich, high-quality Telegram Music & Utility Bot built with Pyrogram & PyTgCalls.</b>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?style=for-the-badge&logo=python" /></a>
  <a href="https://github.com/Pyrogram/Pyrogram"><img src="https://img.shields.io/badge/Framework-Pyrogram-red?style=for-the-badge&logo=telegram" /></a>
  <a href="https://github.com/alonepro098/musicbot"><img src="https://img.shields.io/badge/Version-v2.5%20Pro-purple?style=for-the-badge" /></a>
</p>

---

## ✨ Features

- 🎧 **Multi-Platform Audio & Video Streaming**: YouTube, Spotify, Apple Music, Resso, SoundCloud, Live Streams, M3U8, Index links.
- 🎛️ **Futuristic Player Controls**: Inline buttons for Play, Pause, Resume, Replay, Skip, Stop, Speed (0.5x to 2.0x), and Seek.
- 📥 **Direct Media Downloader**: `/song` and `/video` commands to download directly from YouTube.
- 📜 **Song Lyrics Finder**: `/lyrics` to fetch live synced lyrics for any track.
- 🤖 **Smart AI Assistant**: `/ask` and `/ai` commands powered by AI engines.
- 🎙️ **Text-to-Speech**: `/tts` text conversion to natural voice audio.
- 🎲 **Interactive Group Utilities**: `/quote`, `/shayari`, `/joke`, `/truth`, `/dare`, `/qr`.
- 🧹 **Automatic Storage Cleaner**: Safe cache cleanup with `/clean` or `/clearcache`.
- 🌐 **Multi-Language Support**: English, Hindi, Punjabi, Arabic.
- 🛡️ **Advanced Admin & Sudo Protection**: Sudoers management, Global Ban (`/gban`), Blacklist chats/users, Auth users.

---

## 🚀 Deployment

### 1. One-Click Heroku Deploy

<p align="center">
  <a href="https://dashboard.heroku.com/new?template=https://github.com/alonepro098/musicbot">
    <img src="https://img.shields.io/badge/Deploy%20To%20Heroku-purple?style=for-the-badge&logo=heroku" width="220" />
  </a>
</p>

---

### 2. VPS / Local Deployment

```bash
# Update and install dependencies
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install python3-pip ffmpeg git -y

# Clone the repository
git clone https://github.com/alonepro098/musicbot
cd musicbot

# Install python requirements
pip3 install -U -r requirements.txt

# Configure your environment
cp sample.env .env
nano .env

# Run the Bot
bash start
```

---

## 🛠️ Required Environment Variables

| Variable | Description |
| :--- | :--- |
| `API_ID` | Your Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Your Telegram API Hash |
| `BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `MONGO_DB_URI` | MongoDB Connection URL from [MongoDB Atlas](https://www.mongodb.com/atlas) |
| `LOGGER_ID` | Telegram Channel/Group ID for logging bot activity |
| `OWNER_ID` | Telegram User ID of the Bot Owner |
| `STRING_SESSION` | Pyrogram String Session for the Assistant account |

---

## 📖 Command Guide

### 🎵 Playback Commands
- `/play [song name/link]` - Stream audio on video chat
- `/vplay [song name/link]` - Stream video on video chat
- `/pause` - Pause the streaming track
- `/resume` - Resume the paused stream
- `/skip` - Skip to the next queued track
- `/end` or `/stop` - Stop streaming and clear queue
- `/speed [0.5x - 2.0x]` - Control playback speed
- `/seek [seconds]` - Seek playback time

### 🛠️ Smart Tools
- `/song [query]` - Download MP3 audio directly
- `/video [query]` - Download MP4 video directly
- `/lyrics [song]` - Search lyrics for any song
- `/ask [prompt]` - Ask smart AI query
- `/tts [text]` - Convert text to voice audio
- `/quote` / `/shayari` / `/joke` - Get fun content
- `/ping` - Check latency and server stats

---

<h3 align="center">
  <b>Made with ❤️ by <a href="https://t.me/moh_maya_official">Ayush</a></b>
</h3>
