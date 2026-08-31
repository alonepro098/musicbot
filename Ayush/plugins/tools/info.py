from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app
from config import BANNED_USERS


@app.on_message(filters.command(["id", "chatid"]) & ~BANNED_USERS)
async def id_info_handler(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else "Unknown"

    text = f"<blockquote>🆔 <b><u>ɪᴅ ɪɴғᴏʀᴍᴀᴛɪᴏɴ :</u></b>\n\n"
    text += f"💬 <b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{chat_id}</code>\n"
    text += f"👤 <b>ʏᴏᴜʀ ɪᴅ :</b> <code>{user_id}</code>\n"

    if message.reply_to_message:
        replied_user = message.reply_to_message.from_user
        if replied_user:
            text += f"🎯 <b>ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ :</b> <code>{replied_user.id}</code>\n"
        if message.reply_to_message.forward_from:
            text += f"⏩ <b>ғᴏʀᴡᴀʀᴅ ᴜsᴇʀ ɪᴅ :</b> <code>{message.reply_to_message.forward_from.id}</code>\n"
        if message.reply_to_message.forward_from_chat:
            text += f"📢 <b>ғᴏʀᴡᴀʀᴅ ᴄʜᴀᴛ ɪᴅ :</b> <code>{message.reply_to_message.forward_from_chat.id}</code>\n"

    text += "</blockquote>"
    await message.reply_text(text)


@app.on_message(filters.command(["info", "userinfo"]) & ~BANNED_USERS)
async def user_info_handler(client, message: Message):
    user = None
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        query = message.text.split(None, 1)[1]
        try:
            user = await client.get_users(query)
        except Exception:
            return await message.reply_text("<blockquote>❌ <b>ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.</b></blockquote>")
    else:
        user = message.from_user

    if not user:
        return await message.reply_text("<blockquote>❌ <b>ᴜɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴜsᴇʀ.</b></blockquote>")

    status = "👤 ᴜsᴇʀ"
    if user.is_bot:
        status = "🤖 ʙᴏᴛ"
    if user.is_premium:
        status += " ⭐ ᴘʀᴇᴍɪᴜᴍ"

    text = (
        f"<blockquote>👤 <b><u>ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ :</u></b>\n\n"
        f"🏷️ <b>ғɪʀsᴛ ɴᴀᴍᴇ :</b> {user.first_name}\n"
        f"🏷️ <b>ʟᴀsᴛ ɴᴀᴍᴇ :</b> {user.last_name or 'N/A'}\n"
        f"🔗 <b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{user.username if user.username else 'N/A'}\n"
        f"🆔 <b>ᴜsᴇʀ ɪᴅ :</b> <code>{user.id}</code>\n"
        f"⚡ <b>sᴛᴀᴛᴜs :</b> {status}\n"
        f"🔗 <b>ᴘᴇʀᴍᴀʟɪɴᴋ :</b> {user.mention}</blockquote>"
    )

    await message.reply_text(text)
