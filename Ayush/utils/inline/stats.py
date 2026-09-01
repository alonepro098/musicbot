from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def stats_buttons(_, status):
    not_sudo = [
        InlineKeyboardButton(
            text="ᴏᴠᴇʀᴀʟʟ sᴛᴀᴛs",
            callback_data="TopOverall",
        )
    ]
    sudo = [
        InlineKeyboardButton(
            text="ɢᴇɴᴇʀᴀʟ",
            callback_data="bot_stats_sudo",
        ),
        InlineKeyboardButton(
            text="ᴏᴠᴇʀᴀʟʟ",
            callback_data="TopOverall",
        ),
    ]
    upl = InlineKeyboardMarkup(
        [
            sudo if status else not_sudo,
            [
                InlineKeyboardButton(
                    text="ʙᴀᴄᴋ",
                    callback_data="settingsback_helper",
                ),
                InlineKeyboardButton(
                    text="ᴄʟᴏsᴇ",
                    callback_data="close",
                ),
            ],
        ]
    )
    return upl


def back_stats_buttons(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="ʙᴀᴄᴋ",
                    callback_data="stats_back",
                ),
                InlineKeyboardButton(
                    text="ᴄʟᴏsᴇ",
                    callback_data="close",
                ),
            ],
        ]
    )
    return upl
