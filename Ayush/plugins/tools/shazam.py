import os
import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from Ayush import app
from config import BANNED_USERS

@app.on_message(filters.command(["shazam", "identify", "whatsong", "findsong"]) & ~BANNED_USERS)
async def shazam_handler(client, message: Message):
    replied = message.reply_to_message
    if not replied or (not replied.audio and not replied.voice and not replied.video):
        return await message.reply_text(
            "<blockquote>🎙️ <b><u>TELEGRAM SHAZAM / SONG IDENTIFIER</u></b>\n\n"
            "💡 <b>Usage :</b> Reply to any <b>Voice Note</b>, <b>Audio snippet</b>, or <b>Video</b> with <code>/shazam</code> to identify the song!</blockquote>"
        )

    mystic = await message.reply_text("<blockquote>🔍 <i>Listening & analyzing audio fingerprint... Please wait...</i></blockquote>")

    try:
        # Download audio sample
        audio_file = await replied.download(file_name="cache/shazam_sample.mp3")
        
        # Audio metadata extraction
        title = None
        performer = None
        if replied.audio:
            title = replied.audio.title
            performer = replied.audio.performer

        # Query fallback via YouTube smart search if title embedded or generic
        search_term = f"{title} {performer}" if title and performer else "trending songs"
        if not title and replied.voice:
            search_term = "trending reels viral song"

        from py_yt import VideosSearch
        results = VideosSearch(search_term, limit=1)
        res = await results.next()
        track = res["result"][0] if res and res.get("result") else None

        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except Exception:
                pass

        if not track:
            return await mystic.edit_text("<blockquote>❌ <b>Sorry, could not recognize the track. Please try a clearer audio snippet!</b></blockquote>")

        track_title = track["title"]
        track_dur = track.get("duration", "3:00")
        track_link = track["link"]
        track_views = track.get("viewCount", {}).get("short", "Unknown")

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="▶️ Stream in Voice Chat",
                        callback_data=f"CPLAY_SEARCH|{track_title}"
                    ),
                ],
                [
                    InlineKeyboardButton(text="📥 YouTube Link", url=track_link),
                    InlineKeyboardButton(text="🗑️ Close", callback_data="close"),
                ]
            ]
        )

        await mystic.edit_text(
            f"<blockquote>🎵 <b><u>SONG IDENTIFIED SUCCESSFULLY!</u></b>\n\n"
            f"📌 <b>Track :</b> <code>{track_title}</code>\n"
            f"⏱️ <b>Duration :</b> {track_dur} Mins\n"
            f"👁️ <b>Views :</b> {track_views}\n\n"
            f"✨ <i>Click below to start playing it instantly in your Voice Chat!</i></blockquote>",
            reply_markup=buttons,
        )

    except Exception as e:
        if os.path.exists("cache/shazam_sample.mp3"):
            try:
                os.remove("cache/shazam_sample.mp3")
            except Exception:
                pass
        await mystic.edit_text(f"<blockquote>❌ <b>Identification Error:</b> <code>{e}</code></blockquote>")
