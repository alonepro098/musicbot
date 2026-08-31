from pyrogram.types import InlineKeyboardButton

import config
from Ayush import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="⚡ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⚡",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="💬 sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT),
            InlineKeyboardButton(text="📢 ᴜᴘᴅᴀᴛᴇs", url=config.SUPPORT_CHANNEL),
        ],
        [
            InlineKeyboardButton(text="🛑 [ ᴅᴀɴɢᴇʀ: ᴇᴍᴇʀɢᴇɴᴄʏ sᴜᴘᴘᴏʀᴛ ]", url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="⚡ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⚡",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="📖 ᴄᴏᴍᴍᴀɴᴅs", callback_data="settings_back_helper"),
            InlineKeyboardButton(text="⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings_helper"),
        ],
        [
            InlineKeyboardButton(text="🎛️ ᴀᴜᴅɪᴏ ғɪʟᴛᴇʀs", callback_data="help_callback hb19"),
            InlineKeyboardButton(text="🎙️ ᴠᴄ ᴛᴏᴏʟs", callback_data="help_callback hb20"),
        ],
        [
            InlineKeyboardButton(text="💬 sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT),
            InlineKeyboardButton(text="📢 ᴄʜᴀɴɴᴇʟ", url=config.SUPPORT_CHANNEL),
        ],
        [
            InlineKeyboardButton(text="👑 ᴅᴇᴠᴇʟᴏᴘᴇʀ", user_id=config.OWNER_ID),
            InlineKeyboardButton(text="🚀 sᴏᴜʀᴄᴇ", callback_data="gib_source"),
        ],
        [
            InlineKeyboardButton(text="🛑 [ ᴅᴀɴɢᴇʀ: sʏsᴛᴇᴍ ɪɴғᴏ & ᴢᴏɴᴇ ]", callback_data="bot_info_data"),
        ],
    ]
    return buttons




