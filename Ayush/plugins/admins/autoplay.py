from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app
from Ayush.utils.database import is_autoplay, autoplay_on, autoplay_off
from Ayush.utils.decorators import AdminRightsCheck
from config import BANNED_USERS


@app.on_message(filters.command(["autoplay", "smartplay", "moodplay"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def autoplay_command_handler(cli, message: Message, chat_id, _):
    if len(message.command) < 2:
        is_on = await is_autoplay(chat_id)
        status_str = "<b>ᴇɴᴀʙʟᴇᴅ (ᴏɴ)</b>" if is_on else "<b>ᴅɪsᴀʙʟᴇᴅ (ᴏғғ)</b>"
        btn_text = "ᴛᴜʀɴ ᴏғғ" if is_on else "ᴛᴜʀɴ ᴏɴ"
        btn_data = "AUTOPLAY_OFF" if is_on else "AUTOPLAY_ON"
        
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=btn_text, callback_data=btn_data),
                    InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
                ]
            ]
        )
        return await message.reply_text(
            f"<blockquote>📻 <b><u>sᴍᴀʀᴛ ᴀᴜᴛᴏ-ᴘʟᴀʏ sʏsᴛᴇᴍ</u></b>\n\n"
            f"✨ <b>sᴛᴀᴛᴜs :</b> {status_str}\n\n"
            f"💡 <i>ᴡʜᴇɴ ᴇɴᴀʙʟᴇᴅ, ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ sᴇɴsᴇ ᴛʜᴇ ᴍᴏᴏᴅ/ɢᴇɴʀᴇ ᴏғ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ sᴏɴɢ (ᴇ.ɢ. ʀᴏᴍᴀɴᴛɪᴄ, ᴘᴀʀᴛʏ, ʟᴏ-ғɪ) ᴀɴᴅ ᴋᴇᴇᴘ ᴘʟᴀʏɪɴɢ sɪᴍɪʟᴀʀ ᴛʀᴀᴄᴋs ᴡɪᴛʜᴏᴜᴛ sᴛᴏᴘᴘɪɴɢ!</i></blockquote>",
            reply_markup=buttons,
        )

    state = message.command[1].lower()
    if state in ["on", "enable", "activate", "true"]:
        await autoplay_on(chat_id)
        await message.reply_text(
            "<blockquote><b><u>ᴀᴜᴛᴏ-ᴘʟᴀʏ ᴇɴᴀʙʟᴇᴅ</u></b>\n\n"
            "✨ <i>sᴍᴀʀᴛ ᴍᴏᴏᴅ & sɪᴍɪʟᴀʀ sᴏɴɢs ᴀᴜᴛᴏᴘʟᴀʏ ɪs ɴᴏᴡ ᴀᴄᴛɪᴠᴇ. ɴᴇᴠᴇʀ-ᴇɴᴅɪɴɢ ᴍᴜsɪᴄ ᴠɪʙᴇs !</i></blockquote>"
        )
    elif state in ["off", "disable", "deactivate", "false"]:
        await autoplay_off(chat_id)
        await message.reply_text(
            "<blockquote><b><u>ᴀᴜᴛᴏ-ᴘʟᴀʏ ᴅɪsᴀʙʟᴇᴅ</u></b>\n\n"
            "❌ <i>ᴀᴜᴛᴏ-ᴘʟᴀʏ sᴛᴏᴘᴘᴇᴅ. ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ʟᴇᴀᴠᴇ ᴡʜᴇɴ ǫᴜᴇᴜᴇ ᴇɴᴅs.</i></blockquote>"
        )
    else:
        await message.reply_text("<blockquote>💡 <b>ᴜsᴀɢᴇ :</b> <code>/autoplay [on | off]</code></blockquote>")


@app.on_callback_query(filters.regex(r"^AUTOPLAY_") & ~BANNED_USERS)
async def autoplay_callback_handler(cli, CallbackQuery):
    data_parts = CallbackQuery.data.split("|")
    action_part = data_parts[0].split("_")[1]
    chat_id = int(data_parts[1]) if len(data_parts) > 1 else CallbackQuery.message.chat.id

    if action_part == "ON":
        await autoplay_on(chat_id)
        text = "<b>ᴀᴜᴛᴏ-ᴘʟᴀʏ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ !</b>"
    elif action_part == "OFF":
        await autoplay_off(chat_id)
        text = "<b>ᴀᴜᴛᴏ-ᴘʟᴀʏ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ !</b>"
    else:
        # STATUS
        text = "💡 <i>ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴛᴏɢɢʟᴇ ᴀᴜᴛᴏ-ᴘʟᴀʏ sᴛᴀᴛᴇ :</i>"

    is_on = await is_autoplay(chat_id)
    btn_text = "ᴛᴜʀɴ ᴏғғ" if is_on else "ᴛᴜʀɴ ᴏɴ"
    btn_data = f"AUTOPLAY_OFF|{chat_id}" if is_on else f"AUTOPLAY_ON|{chat_id}"

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=btn_text, callback_data=btn_data),
                InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
            ]
        ]
    )

    try:
        await CallbackQuery.edit_message_text(
            f"<blockquote>📻 <b><u>sᴍᴀʀᴛ ᴀᴜᴛᴏ-ᴘʟᴀʏ sʏsᴛᴇᴍ</u></b>\n\n"
            f"✨ <b>sᴛᴀᴛᴜs :</b> {'🟢 <b>ᴇɴᴀʙʟᴇᴅ (ᴏɴ)</b>' if is_on else '🔴 <b>ᴅɪsᴀʙʟᴇᴅ (ᴏғғ)</b>'}\n\n"
            f"{text}</blockquote>",
            reply_markup=buttons,
        )
    except Exception:
        await CallbackQuery.answer(f"AutoPlay: {'Enabled' if is_on else 'Disabled'}", show_alert=True)

