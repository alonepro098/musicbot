import os
import re
import asyncio
import aiohttp
import aiofiles
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from py_yt import VideosSearch

from Ayush import app
from config import BANNED_USERS, SONG_DOWNLOAD_DURATION, SONG_DOWNLOAD_DURATION_LIMIT


def format_duration(seconds):
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


@app.on_message(filters.command(["song", "music", "mp3"]) & ~BANNED_USERS)
async def song_downloader(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<blockquote><b>💡 <u>ᴜsᴀɢᴇ :</u></b>\n\n<code>/song [sᴏɴɢ ɴᴀᴍᴇ ᴏʀ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ]</code></blockquote>"
        )

    query = message.text.split(None, 1)[1]
    m = await message.reply_text("<blockquote>🔎 <b>sᴇᴀʀᴄʜɪɴɢ ғᴏʀ ʏᴏᴜʀ sᴏɴɢ...</b></blockquote>")

    try:
        results = VideosSearch(query, limit=1)
        res = (await results.next())["result"]
        if not res:
            return await m.edit_text("<blockquote>❌ <b>ɴᴏ sᴏɴɢs ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ǫᴜᴇʀʏ.</b></blockquote>")

        track = res[0]
        title = track.get("title", "Audio Track")
        duration = track.get("duration", "0:00")
        link = track.get("link", "")
        videoid = track.get("id", "")
        views = track.get("viewCount", {}).get("short", "Unknown")
        channel = track.get("channel", {}).get("name", "Unknown Artist")
        thumbnail = track.get("thumbnails", [{}])[0].get("url", "").split("?")[0]

        await m.edit_text(f"<blockquote>⚡ <b>ғᴏᴜɴᴅ :</b> <code>{title[:40]}</code>\n\n📥 <b>ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ...</b></blockquote>")

        # Download thumbnail
        thumb_path = f"cache/thumb_{videoid}.jpg"
        if thumbnail:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(thumbnail) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(thumb_path, mode="wb")
                            await f.write(await resp.read())
                            await f.close()
            except Exception:
                thumb_path = None
        else:
            thumb_path = None

        audio_file = f"cache/{videoid}.mp3"
        
        # Download audio using yt-dlp
        cmd = f'yt-dlp -x --audio-format mp3 -o "{audio_file}" --geo-bypass "{link}" --no-playlist'
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

        if not os.path.exists(audio_file):
            if os.path.exists(f"cache/{videoid}.m4a"):
                audio_file = f"cache/{videoid}.m4a"
            elif os.path.exists(f"cache/{videoid}.opus"):
                audio_file = f"cache/{videoid}.opus"

        if not os.path.exists(audio_file):
            return await m.edit_text("<blockquote>❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴀᴜᴅɪᴏ ғɪʟᴇ.</b></blockquote>")

        caption = (
            f"<blockquote>🎵 <b><u>{title}</u></b>\n\n"
            f"👤 <b>ᴀʀᴛɪsᴛ :</b> {channel}\n"
            f"⏱️ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b> {duration}\n"
            f"👀 <b>ᴠɪᴇᴡs :</b> {views}\n\n"
            f"✨ <b>ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {message.from_user.mention if message.from_user else 'User'}</blockquote>"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="👀 ʏᴏᴜᴛᴜʙᴇ", url=link),
                    InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
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

        # Cleanup
        if os.path.exists(audio_file):
            os.remove(audio_file)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)

    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>ᴇʀʀᴏʀ :</b> <code>{e}</code></blockquote>")


@app.on_message(filters.command(["video", "vdown", "mp4"]) & ~BANNED_USERS)
async def video_downloader(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<blockquote><b>💡 <u>ᴜsᴀɢᴇ :</u></b>\n\n<code>/video [ᴠɪᴅᴇᴏ ɴᴀᴍᴇ ᴏʀ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ]</code></blockquote>"
        )

    query = message.text.split(None, 1)[1]
    m = await message.reply_text("<blockquote>🔎 <b>sᴇᴀʀᴄʜɪɴɢ ғᴏʀ ʏᴏᴜʀ ᴠɪᴅᴇᴏ...</b></blockquote>")

    try:
        results = VideosSearch(query, limit=1)
        res = (await results.next())["result"]
        if not res:
            return await m.edit_text("<blockquote>❌ <b>ɴᴏ ᴠɪᴅᴇᴏs ғᴏᴜɴᴅ.</b></blockquote>")

        track = res[0]
        title = track.get("title", "Video Track")
        duration = track.get("duration", "0:00")
        link = track.get("link", "")
        videoid = track.get("id", "")
        views = track.get("viewCount", {}).get("short", "Unknown")
        channel = track.get("channel", {}).get("name", "Unknown Channel")
        thumbnail = track.get("thumbnails", [{}])[0].get("url", "").split("?")[0]

        await m.edit_text(f"<blockquote>⚡ <b>ғᴏᴜɴᴅ :</b> <code>{title[:40]}</code>\n\n📥 <b>ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ...</b></blockquote>")

        # Download thumbnail
        thumb_path = f"cache/thumb_{videoid}.jpg"
        if thumbnail:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(thumbnail) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(thumb_path, mode="wb")
                            await f.write(await resp.read())
                            await f.close()
            except Exception:
                thumb_path = None
        else:
            thumb_path = None

        video_file = f"cache/{videoid}.mp4"
        cmd = f'yt-dlp -f "best[ext=mp4][height<=720]/best[ext=mp4]/best" -o "{video_file}" --geo-bypass "{link}" --no-playlist'
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

        if not os.path.exists(video_file):
            return await m.edit_text("<blockquote>❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴠɪᴅᴇᴏ.</b></blockquote>")

        caption = (
            f"<blockquote>🎬 <b><u>{title}</u></b>\n\n"
            f"👤 <b>ᴄʜᴀɴɴᴇʟ :</b> {channel}\n"
            f"⏱️ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b> {duration}\n"
            f"👀 <b>ᴠɪᴇᴡs :</b> {views}\n\n"
            f"✨ <b>ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {message.from_user.mention if message.from_user else 'User'}</blockquote>"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="👀 ʏᴏᴜᴛᴜʙᴇ", url=link),
                    InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
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

        # Cleanup
        if os.path.exists(video_file):
            os.remove(video_file)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)

    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>ᴇʀʀᴏʀ :</b> <code>{e}</code></blockquote>")
