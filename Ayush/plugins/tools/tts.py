import os
import aiofiles
import aiohttp
from pyrogram import filters
from pyrogram.types import Message

from Ayush import app
from config import BANNED_USERS


@app.on_message(filters.command(["tts", "voice"]) & ~BANNED_USERS)
async def text_to_speech(client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "<blockquote><b>💡 <u>ᴜsᴀɢᴇ :</u></b>\n\n<code>/tts [ᴛᴇxᴛ ᴛᴏ sᴘᴇᴀᴋ]</code>\n<i>ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ /tts</i></blockquote>"
        )

    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    else:
        text = message.text.split(None, 1)[1]

    if len(text) > 300:
        text = text[:300]

    m = await message.reply_text("<blockquote>🎙️ <b>ɢᴇɴᴇʀᴀᴛɪɴɢ ᴠᴏɪᴄᴇ...</b></blockquote>")

    try:
        # Google Translate TTS API
        lang = "en"
        # If text contains hindi characters
        if any("\u0900" <= c <= "\u097f" for c in text):
            lang = "hi"

        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text}&tl={lang}&client=tw-ob"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

        tts_file = f"cache/tts_{message.id}.mp3"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    async with aiofiles.open(tts_file, mode="wb") as f:
                        await f.write(await resp.read())

        if os.path.exists(tts_file):
            await m.delete()
            await message.reply_audio(
                audio=tts_file,
                caption=f"<blockquote>🎙️ <b>ᴛᴛs ᴠᴏɪᴄᴇ :</b> <code>{text[:60]}...</code></blockquote>",
                title=f"TTS: {text[:20]}",
                performer=app.name,
            )
            os.remove(tts_file)
        else:
            await m.edit_text("<blockquote>❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴛᴛs ᴀᴜᴅɪᴏ.</b></blockquote>")

    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>ᴇʀʀᴏʀ :</b> <code>{e}</code></blockquote>")
