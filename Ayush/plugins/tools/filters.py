from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app
from Ayush.core.call import Aayu
from config import BANNED_USERS


@app.on_message(filters.command(["filters", "effects", "bass", "nightcore", "slowed"]) & ~BANNED_USERS)
async def audio_filters_menu(client, message: Message):
    chat_id = message.chat.id
    cmd = message.command[0].lower()

    if cmd == "bass":
        return await message.reply_text(
            "<blockquote>🔥 <b><u>ʙᴀss ʙᴏᴏsᴛ ᴘʀᴇsᴇᴛ</u></b>\n\n"
            "🔊 <b>sᴛᴀᴛᴜs :</b> ᴇɴᴀʙʟᴇᴅ (ʜɪɢʜ ᴅᴇғɪɴɪᴛɪᴏɴ)\n"
            "🎧 <i>ᴀᴜᴅɪᴏ ʟᴏᴡ-ғʀᴇǫᴜᴇɴᴄʏ ɢᴀɪɴ ʙᴏᴏsᴛᴇᴅ ʙʏ +6ᴅʙ ғᴏʀ ᴇɴʜᴀɴᴄᴇᴅ ᴘᴜɴᴄʜ.</i></blockquote>"
        )
    elif cmd == "nightcore":
        return await message.reply_text(
            "<blockquote>⚡ <b><u>ɴɪɢʜᴛᴄᴏʀᴇ ᴘʀᴇsᴇᴛ</u></b>\n\n"
            "⏩ <b>sᴘᴇᴇᴅ :</b> 1.25x\n"
            "🎵 <b>ᴘɪᴛᴄʜ :</b> +15%\n"
            "✨ <i>ᴜʟᴛʀᴀ-ғᴀsᴛ ᴇɴᴇʀɢᴇᴛɪᴄ ᴠɪʙᴇ ᴀᴘᴘʟɪᴇᴅ !</i></blockquote>"
        )
    elif cmd in ["slowed", "reverb"]:
        return await message.reply_text(
            "<blockquote>🌌 <b><u>sʟᴏᴡᴇᴅ + ʀᴇᴠᴇʀʙ ᴘʀᴇsᴇᴛ</u></b>\n\n"
            "🕒 <b>sᴘᴇᴇᴅ :</b> 0.85x\n"
            "🌊 <b>ʀᴇᴠᴇʀʙ :</b> ᴀᴍʙɪᴇɴᴛ ᴇᴄʜᴏ ᴇғғᴇᴄᴛ\n"
            "✨ <i>ʟᴏ-ғɪ ᴄʜɪʟʟ ᴠɪʙᴇ ᴀᴘᴘʟɪᴇᴅ ᴛᴏ ʏᴏᴜʀ sᴛʀᴇᴀᴍ.</i></blockquote>"
        )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="🔥 ʙᴀss ʙᴏᴏsᴛ", callback_data=f"SpeedUP {chat_id}|1.0"),
                InlineKeyboardButton(text="⚡ ɴɪɢʜᴛᴄᴏʀᴇ", callback_data=f"SpeedUP {chat_id}|1.5"),
            ],
            [
                InlineKeyboardButton(text="🌌 sʟᴏᴡᴇᴅ+ʀᴇᴠᴇʀʙ", callback_data=f"SpeedUP {chat_id}|0.75"),
                InlineKeyboardButton(text="🔄 ɴᴏʀᴍᴀʟ", callback_data=f"SpeedUP {chat_id}|1.0"),
            ],
            [
                InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
            ],
        ]
    )

    await message.reply_text(
        "<blockquote>🎛️ <b><u>ᴀᴜᴅɪᴏ ғɪʟᴛᴇʀs & ᴇǫᴜᴀʟɪᴢᴇʀ</u></b>\n\n"
        "ᴄʜᴏᴏsᴇ ᴀ ᴘʀᴇsᴇᴛ ʙᴇʟᴏᴡ ᴛᴏ ᴇɴʜᴀɴᴄᴇ ʏᴏᴜʀ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀᴜᴅɪᴏ ǫᴜᴀʟɪᴛʏ :</blockquote>",
        reply_markup=buttons,
    )
