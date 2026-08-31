from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app, YouTube
from Ayush.core.call import Aayu
from Ayush.utils.database import mongodb, get_lang
from strings import get_string
from config import BANNED_USERS

introdb = mongodb.intro_themes

@app.on_message(filters.command(["setintro", "setmyintro"]) & ~BANNED_USERS)
async def set_intro_handler(client, message: Message):
    user_id = message.from_user.id
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "<blockquote>👑 <b><u>VIP CUSTOM ENTRY THEME</u></b>\n\n"
            "💡 <b>Usage :</b> <code>/setintro [song name or YT link]</code>\n"
            "Or reply to any audio file with <code>/setintro</code>!</blockquote>"
        )

    if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.voice):
        query = message.reply_to_message.audio.title if message.reply_to_message.audio else "Custom Voice Theme"
    else:
        query = " ".join(message.command[1:])

    await introdb.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "name": message.from_user.first_name, "query": query}},
        upsert=True,
    )
    await message.reply_text(
        f"<blockquote>👑 <b><u>VIP INTRO THEME SAVED</u></b>\n\n"
        f"👤 <b>User :</b> {message.from_user.mention}\n"
        f"🎵 <b>Anthem :</b> <code>{query}</code>\n\n"
        f"✨ <i>Whenever you or an admin types <code>/intro</code> in group, your royal entrance anthem will play in Voice Chat!</i></blockquote>"
    )


@app.on_message(filters.command(["myintro"]) & ~BANNED_USERS)
async def my_intro_handler(client, message: Message):
    user_id = message.from_user.id
    data = await introdb.find_one({"user_id": user_id})
    if not data:
        return await message.reply_text("<blockquote>❌ <b>You haven't set an intro theme yet!</b>\nSet one with <code>/setintro [song name]</code></blockquote>")

    await message.reply_text(
        f"<blockquote>👑 <b><u>YOUR VIP INTRO THEME</u></b>\n\n"
        f"🎵 <b>Theme :</b> <code>{data['query']}</code>\n"
        f"💡 <i>Type <code>/intro</code> in group to play it in VC!</i></blockquote>"
    )


@app.on_message(filters.command(["delintro", "delmyintro"]) & ~BANNED_USERS)
async def del_intro_handler(client, message: Message):
    user_id = message.from_user.id
    await introdb.delete_one({"user_id": user_id})
    await message.reply_text("<blockquote>🗑️ <b>Your VIP Intro Theme has been removed.</b></blockquote>")


@app.on_message(filters.command(["intro", "playintro"]) & filters.group & ~BANNED_USERS)
async def play_intro_handler(client, message: Message):
    target_user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    if len(message.command) > 1 and message.entities:
        for ent in message.entities:
            if ent.type.name == "MENTION":
                mention_text = message.text[ent.offset:ent.offset+ent.length].replace("@", "")
                try:
                    target_user = await app.get_users(mention_text)
                    break
                except Exception:
                    pass

    data = await introdb.find_one({"user_id": target_user.id})
    if not data:
        return await message.reply_text(
            f"<blockquote>❌ <b>{target_user.mention} hasn't set an intro theme yet!</b>\n"
            f"Set using <code>/setintro [song name]</code></blockquote>"
        )

    chat_id = message.chat.id
    theme_query = data["query"]
    mystic = await message.reply_text(
        f"<blockquote>👑 <b><u>VIP ENTRANCE ANNOUNCEMENT</u></b>\n\n"
        f"🎺 <i>Make way for {target_user.mention}! Loading their grand entrance theme...</i></blockquote>"
    )

    try:
        from py_yt import VideosSearch
        results = VideosSearch(theme_query, limit=1)
        res = await results.next()
        track = res["result"][0]
        vidid = track["id"]
        title = track["title"]

        language = await get_lang(chat_id)
        _ = get_string(language)

        from Ayush.utils.stream.stream import stream
        await stream(
            _,
            mystic,
            target_user.id,
            f"https://www.youtube.com/watch?v={vidid}",
            chat_id,
            f"👑 VIP Entry ({target_user.first_name})",
            chat_id,
            video=None,
            streamtype="youtube",
        )
    except Exception as e:
        await mystic.edit_text(f"<blockquote>❌ <b>Error playing intro theme:</b> <code>{e}</code></blockquote>")
