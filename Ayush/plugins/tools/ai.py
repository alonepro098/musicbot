import urllib.parse
import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app
from config import BANNED_USERS


async def fetch_ai_answer(query: str) -> str:
    encoded = urllib.parse.quote(query)
    
    # 1. DuckDuckGo Instant Knowledge
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.duckduckgo.com/?q={encoded}&format=json", timeout=6) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if data.get("AbstractText"):
                        return data["AbstractText"]
                    if data.get("RelatedTopics") and len(data["RelatedTopics"]) > 0:
                        first_topic = data["RelatedTopics"][0]
                        if isinstance(first_topic, dict) and first_topic.get("Text"):
                            return first_topic["Text"]
    except Exception:
        pass

    # 2. Wikipedia Summary
    try:
        clean_q = query.replace("who is", "").replace("what is", "").replace("tell me about", "").strip()
        w_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_q)}"
        headers = {"User-Agent": "MusicBot/2.0 (https://t.me/AyushMusic)"}
        async with aiohttp.ClientSession() as session:
            async with session.get(w_url, headers=headers, timeout=6) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("extract"):
                        return data["extract"]
    except Exception:
        pass

    # 3. Fallback AI response
    return (
        f"<b>Topic :</b> <code>{query}</code>\n\n"
        f"I am your Music & Utility AI Assistant! I can help you find songs, stream in voice chats, discover artists, download MP3s, and control your group queue. Type <code>/help</code> to explore everything!"
    )


@app.on_message(filters.command(["ask", "ai", "gpt", "bot"]) & ~BANNED_USERS)
async def ai_query_handler(client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "<blockquote><b>💡 <u>USAGE :</u></b>\n\n<code>/ask [your question]</code>\n<i>Or reply to any message with /ask</i></blockquote>"
        )

    if message.reply_to_message and message.reply_to_message.text:
        query = f"{message.reply_to_message.text} " + (" ".join(message.command[1:]) if len(message.command) > 1 else "")
    else:
        query = message.text.split(None, 1)[1]

    m = await message.reply_text("<blockquote>🧠 <b>Thinking...</b></blockquote>")

    try:
        response_text = await fetch_ai_answer(query)
        if len(response_text) > 3800:
            response_text = response_text[:3800] + "..."

        formatted_reply = (
            f"<blockquote>🤖 <b><u>AI RESPONSE :</u></b>\n\n"
            f"{response_text}</blockquote>"
        )

        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="CLOSE", callback_data="close")]]
        )

        await m.edit_text(formatted_reply, reply_markup=buttons)

    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>Error :</b> <code>{e}</code></blockquote>")
