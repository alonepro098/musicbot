from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import SUPPORT_CHAT


def botplaylist_markup(_):
    buttons = [
        [
            InlineKeyboardButton(text="🔵 💬 sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT),
            InlineKeyboardButton(text="🔴 🗑️ ᴄʟᴏsᴇ", callback_data="close"),
        ],
    ]
    return buttons


def close_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🔴 🗑️ ᴄʟᴏsᴇ",
                    callback_data="close",
                ),
            ]
        ]
    )
    return upl


def supp_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🔵 💬 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ",
                    url=SUPPORT_CHAT,
                ),
            ]
        ]
    )
    return upl

