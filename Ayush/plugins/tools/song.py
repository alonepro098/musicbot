import os
import asyncio
import aiohttp
import aiofiles
import yt_dlp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from py_yt import VideosSearch

from Ayush import app
from config import BANNED_USERS


def _download_audio_ytdlp(link: str, out_template: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


def _download_video_ytdlp(link: str, out_template: str):
    ydl_opts = {
        "format": "best[ext=mp4][height<=720]/best[ext=mp4]/best",
        "outtmpl": out_template,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


@app.on_message(filters.command(["song", "music", "mp3", "download"]) & ~BANNED_USERS)
async def song_downloader(client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "<blockquote><b>💡 <u>USAGE :</u></b>\n\n<code>/song [song name or YouTube link]</code></blockquote>"
        )

    query = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else message.text.split(None, 1)[1]
    m = await message.reply_text("<blockquote>🔎 <b>Searching for track...</b></blockquote>")

    try:
        results = VideosSearch(query, limit=1)
        res = (await results.next())["result"]
        if not res:
            return await m.edit_text("<blockquote>❌ <b>No songs found for your query.</b></blockquote>")

        track = res[0]
        title = track.get("title", "Audio Track")
        duration = track.get("duration", "0:00")
        link = track.get("link", "")
        videoid = track.get("id", "")
        views = track.get("viewCount", {}).get("short", "Unknown")
        channel = track.get("channel", {}).get("name", "Unknown Artist")
        thumbnail = track.get("thumbnails", [{}])[0].get("url", "").split("?")[0]

        await m.edit_text(f"<blockquote>⚡ <b>Found :</b> <code>{title[:40]}</code>\n\n📥 <b>Downloading high quality MP3...</b></blockquote>")

        os.makedirs("cache", exist_ok=True)
        thumb_path = f"cache/thumb_{videoid}.jpg"
        if thumbnail:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(thumbnail, timeout=10) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(thumb_path, mode="wb")
                            await f.write(await resp.read())
                            await f.close()
            except Exception:
                thumb_path = None
        else:
            thumb_path = None

        out_tmpl = f"cache/{videoid}.%(ext)s"
        audio_file = f"cache/{videoid}.mp3"

        # Download in thread pool so bot stays fast & non-blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _download_audio_ytdlp, link, out_tmpl)

        if not os.path.exists(audio_file):
            for ext in [".m4a", ".opus", ".webm", ".aac"]:
                if os.path.exists(f"cache/{videoid}{ext}"):
                    audio_file = f"cache/{videoid}{ext}"
                    break

        if not os.path.exists(audio_file):
            return await m.edit_text("<blockquote>❌ <b>Failed to download audio. Please try another track!</b></blockquote>")

        caption = (
            f"<blockquote>🎵 <b><u>{title}</u></b>\n\n"
            f"👤 <b>Artist :</b> {channel}\n"
            f"⏱️ <b>Duration :</b> {duration}\n"
            f"👀 <b>Views :</b> {views}\n\n"
            f"✨ <b>Requested By :</b> {message.from_user.mention if message.from_user else 'User'}</blockquote>"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="YOUTUBE", url=link),
                    InlineKeyboardButton(text="CLOSE", callback_data="close"),
                ]
            ]
        )

        await m.delete()
        await message.reply_audio(
            audio=audio_file,
            caption=caption,
            duration=0,
            performer=channel,
            title=title,
            thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None,
            reply_markup=buttons,
        )

        # Clean cache
        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except Exception:
                pass
        if thumb_path and os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except Exception:
                pass

    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>Error :</b> <code>{e}</code></blockquote>")


@app.on_message(filters.command(["video", "vdown", "mp4"]) & ~BANNED_USERS)
async def video_downloader(client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "<blockquote><b>💡 <u>USAGE :</u></b>\n\n<code>/video [video name or YouTube link]</code></blockquote>"
        )

    query = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else message.text.split(None, 1)[1]
    m = await message.reply_text("<blockquote>🔎 <b>Searching for video...</b></blockquote>")

    try:
        results = VideosSearch(query, limit=1)
        res = (await results.next())["result"]
        if not res:
            return await m.edit_text("<blockquote>❌ <b>No videos found.</b></blockquote>")

        track = res[0]
        title = track.get("title", "Video Track")
        duration = track.get("duration", "0:00")
        link = track.get("link", "")
        videoid = track.get("id", "")
        views = track.get("viewCount", {}).get("short", "Unknown")
        channel = track.get("channel", {}).get("name", "Unknown Channel")
        thumbnail = track.get("thumbnails", [{}])[0].get("url", "").split("?")[0]

        await m.edit_text(f"<blockquote>⚡ <b>Found :</b> <code>{title[:40]}</code>\n\n📥 <b>Downloading HD video...</b></blockquote>")

        os.makedirs("cache", exist_ok=True)
        thumb_path = f"cache/thumb_{videoid}.jpg"
        if thumbnail:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(thumbnail, timeout=10) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(thumb_path, mode="wb")
                            await f.write(await resp.read())
                            await f.close()
            except Exception:
                thumb_path = None
        else:
            thumb_path = None

        out_tmpl = f"cache/{videoid}.%(ext)s"
        video_file = f"cache/{videoid}.mp4"

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _download_video_ytdlp, link, out_tmpl)

        if not os.path.exists(video_file):
            for ext in [".mkv", ".webm"]:
                if os.path.exists(f"cache/{videoid}{ext}"):
                    video_file = f"cache/{videoid}{ext}"
                    break

        if not os.path.exists(video_file):
            return await m.edit_text("<blockquote>❌ <b>Failed to download video.</b></blockquote>")

        caption = (
            f"<blockquote>🎬 <b><u>{title}</u></b>\n\n"
            f"👤 <b>Channel :</b> {channel}\n"
            f"⏱️ <b>Duration :</b> {duration}\n"
            f"👀 <b>Views :</b> {views}\n\n"
            f"✨ <b>Requested By :</b> {message.from_user.mention if message.from_user else 'User'}</blockquote>"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="YOUTUBE", url=link),
                    InlineKeyboardButton(text="CLOSE", callback_data="close"),
                ]
            ]
        )

        await m.delete()
        await message.reply_video(
            video=video_file,
            caption=caption,
            thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None,
            reply_markup=buttons,
        )

        if os.path.exists(video_file):
            try:
                os.remove(video_file)
            except Exception:
                pass
        if thumb_path and os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except Exception:
                pass

    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>Error :</b> <code>{e}</code></blockquote>")
