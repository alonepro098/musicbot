from pyrogram.types import InlineKeyboardButton

import config
from Ayush import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="ADD ME TO YOUR GROUP",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="UPDATES", url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text="OWNER", user_id=config.OWNER_ID),
        ],
        [
            InlineKeyboardButton(text="HELP COMMANDS", callback_data="help_main"),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="ADD ME TO YOUR GROUP",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="UPDATES", url=config.SUPPORT_CHANNEL),
            InlineKeyboardButton(text="OWNER", user_id=config.OWNER_ID),
        ],
        [
            InlineKeyboardButton(text="HELP COMMANDS", callback_data="help_main"),
        ],
        [
            InlineKeyboardButton(text="SETTINGS", callback_data="settings_helper"),
            InlineKeyboardButton(text="SUPPORT", url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons
