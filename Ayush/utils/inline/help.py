from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app


def help_main_markup(_=None):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ᴍᴜsɪᴄ", callback_data="help_cat_music"),
                InlineKeyboardButton(text="ᴇxᴛʀᴀ", callback_data="help_cat_extra"),
            ],
            [
                InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="settingsback_helper"),
                InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close"),
            ],
        ]
    )


def help_pannel(_=None, START=None, page=1):
    return help_main_markup(_)


def help_music_markup(_):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ᴘʟᴀʏ", callback_data="help_callback hb11|music"),
                InlineKeyboardButton(text="ᴘᴀᴜsᴇ / ʀᴇsᴜᴍᴇ", callback_data="help_callback hb1|music"),
            ],
            [
                InlineKeyboardButton(text="sᴋɪᴘ", callback_data="help_callback hb1|music"),
                InlineKeyboardButton(text="sᴛᴏᴘ / ᴇɴᴅ", callback_data="help_callback hb1|music"),
            ],
            [
                InlineKeyboardButton(text="sᴇᴇᴋ", callback_data="help_callback hb13|music"),
                InlineKeyboardButton(text="sᴘᴇᴇᴅ", callback_data="help_callback hb15|music"),
                InlineKeyboardButton(text="ʟᴏᴏᴘ", callback_data="help_callback hb8|music"),
            ],
            [
                InlineKeyboardButton(text="ǫᴜᴇᴜᴇ", callback_data="help_callback hb12|music"),
                InlineKeyboardButton(text="sʜᴜғғʟᴇ", callback_data="help_callback hb12|music"),
            ],
            [
                InlineKeyboardButton(text="ᴅᴏᴡɴʟᴏᴀᴅ", callback_data="help_callback hb14|music"),
                InlineKeyboardButton(text="ʟʏʀɪᴄs", callback_data="help_callback hb17|music"),
            ],
            [
                InlineKeyboardButton(text="ғɪʟᴛᴇʀs", callback_data="help_callback hb19|music"),
                InlineKeyboardButton(text="ᴀᴜᴛᴏᴘʟᴀʏ", callback_data="help_callback hb21|music"),
            ],
            [
                InlineKeyboardButton(text="ʀᴀᴅɪᴏ", callback_data="help_callback hb22|music"),
                InlineKeyboardButton(text="ʀᴇᴇʟs", callback_data="help_callback hb26|music"),
            ],
            [
                InlineKeyboardButton(text="ᴠɪᴘ ɪɴᴛʀᴏ", callback_data="help_callback hb24|music"),
                InlineKeyboardButton(text="ᴠᴄ ᴛᴏᴏʟs", callback_data="help_callback hb20|music"),
            ],
            [
                InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="help_main"),
                InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close"),
            ],
        ]
    )


def help_extra_markup(_):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ᴀᴅᴍɪɴ", callback_data="help_callback hb1|extra"),
                InlineKeyboardButton(text="ᴀᴜᴛʜ", callback_data="help_callback hb2|extra"),
            ],
            [
                InlineKeyboardButton(text="ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="help_callback hb3|extra"),
                InlineKeyboardButton(text="ɢ-ʙᴀɴ", callback_data="help_callback hb7|extra"),
            ],
            [
                InlineKeyboardButton(text="ʙʟ-ᴄʜᴀᴛ", callback_data="help_callback hb4|extra"),
                InlineKeyboardButton(text="ʙʟ-ᴜsᴇʀ", callback_data="help_callback hb5|extra"),
            ],
            [
                InlineKeyboardButton(text="ᴄ-ᴘʟᴀʏ", callback_data="help_callback hb6|extra"),
                InlineKeyboardButton(text="ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="help_callback hb9|extra"),
            ],
            [
                InlineKeyboardButton(text="ᴘɪɴɢ", callback_data="help_callback hb10|extra"),
                InlineKeyboardButton(text="ᴀɪ ᴛᴏᴏʟs", callback_data="help_callback hb16|extra"),
            ],
            [
                InlineKeyboardButton(text="sᴏɴɢ ǫᴜɪᴢ", callback_data="help_callback hb23|extra"),
                InlineKeyboardButton(text="sʜᴀᴢᴀᴍ", callback_data="help_callback hb25|extra"),
            ],
            [
                InlineKeyboardButton(text="sʟᴇᴇᴘ ᴛɪᴍᴇʀ", callback_data="help_callback hb27|extra"),
                InlineKeyboardButton(text="ғᴜɴ & ᴇxᴛʀᴀ", callback_data="help_callback hb18|extra"),
            ],
            [
                InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="help_main"),
                InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close"),
            ],
        ]
    )


def help_back_markup(category="music"):
    target = "help_cat_music" if category == "music" else "help_cat_extra"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data=target),
                InlineKeyboardButton(text="ᴍᴀɪɴ ʜᴇʟᴘ", callback_data="help_main"),
            ],
            [
                InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close"),
            ]
        ]
    )


def private_help_panel(_):
    return [
        [
            InlineKeyboardButton(
                text="ᴏᴘᴇɴ ʜᴇʟᴘ ᴍᴇɴᴜ",
                url=f"https://t.me/{app.username}?start=help",
            )
        ]
    ]
