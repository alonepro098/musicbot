from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app
from Ayush.core.call import Aayu
from config import BANNED_USERS


@app.on_message(filters.command(["vcinfo", "vclink", "vcmembers"]) & ~BANNED_USERS)
async def vc_tools_handler(client, message: Message):
    chat_id = message.chat.id
    cmd = message.command[0].lower()

    if message.chat.type.name in ["PRIVATE", "BOT"]:
        return await message.reply_text("<blockquote>❌ <b>ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs/ᴄʜᴀɴɴᴇʟs.</b></blockquote>")

    try:
        chat = await client.get_chat(chat_id)
        
        if cmd == "vclink":
            if chat.username:
                vclink = f"https://t.me/{chat.username}?videochat"
            else:
                invite = await client.export_chat_invite_link(chat_id)
                vclink = f"{invite}?videochat"

            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="🎙️ ᴊᴏɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ", url=vclink)]]
            )
            return await message.reply_text(
                f"<blockquote>🎙️ <b><u>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪɴᴠɪᴛᴇ ʟɪɴᴋ</u></b>\n\n"
                f"🔗 <b>ʟɪɴᴋ :</b> <a href=\"{vclink}\">ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴊᴏɪɴ</a></blockquote>",
                reply_markup=buttons,
                disable_web_page_preview=True,
            )

        # VC Info
        is_playing = Aayu.is_playing(chat_id) if hasattr(Aayu, "is_playing") else True
        text = (
            f"<blockquote>🎙️ <b><u>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴅɪᴀɢɴᴏsᴛɪᴄs</u></b>\n\n"
            f"🏷️ <b>ᴄʜᴀᴛ :</b> {chat.title}\n"
            f"🆔 <b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{chat_id}</code>\n"
            f"⚡ <b>ʙᴏᴛ sᴛᴀᴛᴜs :</b> {'🟢 sᴛʀᴇᴀᴍɪɴɢ' if is_playing else '🟡 ʀᴇᴀᴅʏ'}\n"
            f"🎧 <b>ᴀᴜᴅɪᴏ ᴇɴɢɪɴᴇ :</b> ᴘʏ-ᴛɢᴄᴀʟʟs v0.8.4\n"
            f"📡 <b>ʙɪᴛʀᴀᴛᴇ :</b> 48ᴋʜᴢ / 320ᴋʙᴘs (sᴛᴇʀᴇᴏ)</blockquote>"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="🚨 ᴇᴍᴇʀɢᴇɴᴄʏ sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
                    InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
                ]
            ]
        )

        await message.reply_text(text, reply_markup=buttons)

    except Exception as e:
        await message.reply_text(f"<blockquote>❌ <b>ᴇʀʀᴏʀ :</b> <code>{e}</code></blockquote>")
