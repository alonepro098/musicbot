from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app


def help_pannel(_, START: Union[bool, int] = None, page: int = 1):
    back_or_close = (
        [InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data="settings_back_helper")]
        if START
        else [InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close")]
    )

    if page == 2:
        menu = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="🏓 ᴘɪɴɢ", callback_data="help_callback hb10"),
                    InlineKeyboardButton(text="🎵 ᴘʟᴀʏ", callback_data="help_callback hb11"),
                    InlineKeyboardButton(text="🔀 sʜᴜғғʟᴇ", callback_data="help_callback hb12"),
                ],
                [
                    InlineKeyboardButton(text="⏩ sᴇᴇᴋ", callback_data="help_callback hb13"),
                    InlineKeyboardButton(text="📥 ᴅᴏᴡɴʟᴏᴀᴅ", callback_data="help_callback hb14"),
                    InlineKeyboardButton(text="⚡ sᴘᴇᴇᴅ", callback_data="help_callback hb15"),
                ],
                [
                    InlineKeyboardButton(text="🤖 ᴀɪ-ᴛᴏᴏʟs", callback_data="help_callback hb16"),
                    InlineKeyboardButton(text="📜 ʟʏʀɪᴄs", callback_data="help_callback hb17"),
                    InlineKeyboardButton(text="🎉 ғᴜɴ & ᴇxᴛʀᴀ", callback_data="help_callback hb18"),
                ],
                [
                    InlineKeyboardButton(text="🎛️ ғɪʟᴛᴇʀs", callback_data="help_callback hb19"),
                    InlineKeyboardButton(text="🎙️ ᴠᴄ ᴛᴏᴏʟs", callback_data="help_callback hb20"),
                ],
                [
                    InlineKeyboardButton(text="◀️ ᴘᴀɢᴇ 1", callback_data="help_page 1"),
                    InlineKeyboardButton(text="🏠 ʜᴏᴍᴇ", callback_data="settingsback_helper"),
                    InlineKeyboardButton(text="▶️ ᴘᴀɢᴇ 1", callback_data="help_page 1"),
                ],
                back_or_close,
            ]
        )

    else:
        menu = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="🛡️ ᴀᴅᴍɪɴ", callback_data="help_callback hb1"),
                    InlineKeyboardButton(text="🔑 ᴀᴜᴛʜ", callback_data="help_callback hb2"),
                    InlineKeyboardButton(text="📢 ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="help_callback hb3"),
                ],
                [
                    InlineKeyboardButton(text="🚫 ʙʟ-ᴄʜᴀᴛ", callback_data="help_callback hb4"),
                    InlineKeyboardButton(text="👤 ʙʟ-ᴜsᴇʀ", callback_data="help_callback hb5"),
                    InlineKeyboardButton(text="📺 ᴄ-ᴘʟᴀʏ", callback_data="help_callback hb6"),
                ],
                [
                    InlineKeyboardButton(text="🔨 ɢ-ʙᴀɴ", callback_data="help_callback hb7"),
                    InlineKeyboardButton(text="🔁 ʟᴏᴏᴘ", callback_data="help_callback hb8"),
                    InlineKeyboardButton(text="🛠️ ᴍᴀɪɴᴛ", callback_data="help_callback hb9"),
                ],
                [
                    InlineKeyboardButton(text="◀️ ᴘᴀɢᴇ 2", callback_data="help_page 2"),
                    InlineKeyboardButton(text="🏠 ʜᴏᴍᴇ", callback_data="settingsback_helper"),
                    InlineKeyboardButton(text="▶️ ᴘᴀɢᴇ 2", callback_data="help_page 2"),
                ],
                back_or_close,
            ]
        )
    return menu


def help_back_markup(_):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴘ", callback_data="settings_back_helper")]]
    )


def private_help_panel(_):
    return [
        [
            InlineKeyboardButton(
                text="📖 ᴏᴘᴇɴ ʜᴇʟᴘ ᴍᴇɴᴜ",
                url=f"https://t.me/{app.username}?start=help",
            )
        ]
    ]

