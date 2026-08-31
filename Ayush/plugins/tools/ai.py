import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app
from config import BANNED_USERS


@app.on_message(filters.command(["ask", "ai", "gpt"]) & ~BANNED_USERS)
async def ai_query_handler(client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "<blockquote><b>💡 <u>ᴜsᴀɢᴇ :</u></b>\n\n<code>/ask [ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴ]</code>\n<i>ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ /ask</i></blockquote>"
        )

    if message.reply_to_message and message.reply_to_message.text:
        query = f"{message.reply_to_message.text} " + (" ".join(message.command[1:]) if len(message.command) > 1 else "")
    else:
        query = message.text.split(None, 1)[1]

    m = await message.reply_text("<blockquote>🧠 <b>ᴛʜɪɴᴋɪɴɢ...</b></blockquote>")

    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response_text = None

        # Free reliable AI endpoint
        async with aiohttp.ClientSession() as session:
            try:
                ai_url = f"https://dark-yasiya-api-new.vercel.app/ai/chatgpt?q={query}"
                async with session.get(ai_url, timeout=12) as r:
                    if r.status == 200:
                        data = await r.json()
                        response_text = data.get("result") or data.get("response") or data.get("reply")
            except Exception:
                pass

            if not response_text:
                try:
                    fallback_url = f"https://itzpire.com/ai/gpt-logic?q={query}"
                    async with session.get(fallback_url, timeout=12) as r:
                        if r.status == 200:
                            data = await r.json()
                            response_text = data.get("data") or data.get("result")
                except Exception:
                    pass

        if not response_text:
            response_text = "I am an advanced music and utility bot! Ask me anything about music, artists, lyrics, or commands."

        if len(response_text) > 3800:
            response_text = response_text[:3800] + "..."

        formatted_reply = (
            f"<blockquote>🤖 <b><u>ᴀɪ ʀᴇsᴘᴏɴsᴇ :</u></b>\n\n"
            f"{response_text}</blockquote>"
        )

        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close")]]
        )

        await m.edit_text(formatted_reply, reply_markup=buttons)

    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>ᴇʀʀᴏʀ :</b> <code>{e}</code></blockquote>")
