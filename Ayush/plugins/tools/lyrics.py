import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app
from config import BANNED_USERS


@app.on_message(filters.command(["lyrics", "lyric"]) & ~BANNED_USERS)
async def lyrics_finder(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "<blockquote><b>💡 <u>ᴜsᴀɢᴇ :</u></b>\n\n<code>/lyrics [sᴏɴɢ ɴᴀᴍᴇ]</code></blockquote>"
        )

    query = message.text.split(None, 1)[1]
    m = await message.reply_text("<blockquote>🔎 <b>sᴇᴀʀᴄʜɪɴɢ ғᴏʀ ʟʏʀɪᴄs...</b></blockquote>")

    try:
        url = f"https://api.lyrics.ovh/v1/{query.replace(' - ', '/') if ' - ' in query else query}"
        async with aiohttp.ClientSession() as session:
            # First try lyrics.ovh
            async with session.get(f"https://lrclib.net/api/search?q={query}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and len(data) > 0:
                        first = data[0]
                        lyrics_text = first.get("plainLyrics") or first.get("syncedLyrics")
                        title = first.get("trackName", query)
                        artist = first.get("artistName", "")

                        if lyrics_text:
                            if len(lyrics_text) > 3800:
                                lyrics_text = lyrics_text[:3800] + "\n\n...[ᴛʀᴜɴᴄᴀᴛᴇᴅ]..."
                            formatted = (
                                f"<blockquote>📜 <b><u>ʟʏʀɪᴄs ғᴏʀ : {title} ({artist})</u></b>\n\n"
                                f"{lyrics_text}</blockquote>"
                            )
                            buttons = InlineKeyboardMarkup(
                                [[InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close")]]
                            )
                            return await m.edit_text(formatted, reply_markup=buttons)

            # Fallback to secondary source
            async with session.get(f"https://some-random-api.com/lyrics?title={query}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    lyrics_text = data.get("lyrics")
                    title = data.get("title", query)
                    artist = data.get("author", "")

                    if lyrics_text:
                        if len(lyrics_text) > 3800:
                            lyrics_text = lyrics_text[:3800] + "\n\n...[ᴛʀᴜɴᴄᴀᴛᴇᴅ]..."
                        formatted = (
                            f"<blockquote>📜 <b><u>ʟʏʀɪᴄs ғᴏʀ : {title} ({artist})</u></b>\n\n"
                            f"{lyrics_text}</blockquote>"
                        )
                        buttons = InlineKeyboardMarkup(
                            [[InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close")]]
                        )
                        return await m.edit_text(formatted, reply_markup=buttons)

        await m.edit_text("<blockquote>❌ <b>ɴᴏ ʟʏʀɪᴄs ғᴏᴜɴᴅ ғᴏʀ ᴛʜɪs sᴏɴɢ.</b></blockquote>")
    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>ᴇʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ʟʏʀɪᴄs :</b> <code>{e}</code></blockquote>")
