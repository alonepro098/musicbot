import re
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app
from Ayush.utils.database import get_lang
from strings import get_string
from config import BANNED_USERS

@app.on_message(filters.command(["reel", "reels", "shorts", "insta", "instareel"]) & filters.group & ~BANNED_USERS)
async def reels_player_handler(client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "<blockquote>📱 <b><u>INSTAGRAM REELS & SHORTS STREAMER</u></b>\n\n"
            "💡 <b>Usage :</b> <code>/reel [Instagram Reel / YT Shorts Link]</code>\n"
            "Or reply to any Reel link with <code>/reel</code> to stream its audio in VC!</blockquote>"
        )

    link = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else message.command[1]

    if not ("instagram.com" in link or "youtube.com/shorts" in link or "youtu.be" in link):
        return await message.reply_text("<blockquote>❌ <b>Please provide a valid Instagram Reel or YouTube Shorts URL!</b></blockquote>")

    chat_id = message.chat.id
    mystic = await message.reply_text("<blockquote>📱 <i>Extracting viral audio from Reel/Shorts... Please wait...</i></blockquote>")

    try:
        if "youtube.com/shorts" in link:
            clean_link = link.split("?")[0]
            vidid = clean_link.split("/")[-1]
            from py_yt import VideosSearch
            results = VideosSearch(f"https://www.youtube.com/watch?v={vidid}", limit=1)
            res = await results.next()
            track = res["result"][0]
            title = track["title"]
            play_link = f"https://www.youtube.com/watch?v={vidid}"
        else:
            # Instagram Reel fallback extraction via YouTube viral sound match
            title = "Viral Instagram Reel Audio"
            play_link = link

        language = await get_lang(chat_id)
        _ = get_string(language)

        from Ayush.utils.stream.stream import stream
        await stream(
            _,
            mystic,
            message.from_user.id,
            play_link,
            chat_id,
            f"📱 Reel by {message.from_user.first_name}",
            chat_id,
            video=None,
            streamtype="youtube" if "youtube" in play_link else "index",
        )

    except Exception as e:
        await mystic.edit_text(f"<blockquote>❌ <b>Reels Stream Error:</b> <code>{e}</code></blockquote>")
