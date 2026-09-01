from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app


def help_main_markup(_=None):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="MUSIC", callback_data="help_cat_music"),
                InlineKeyboardButton(text="EXTRA", callback_data="help_cat_extra"),
            ],
            [
                InlineKeyboardButton(text="BACK", callback_data="settingsback_helper"),
                InlineKeyboardButton(text="CLOSE", callback_data="close"),
            ],
        ]
    )


def help_pannel(_=None, START=None, page=1):
    return help_main_markup(_)



def help_music_markup(_):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="PLAY", callback_data="help_callback hb11|music"),
                InlineKeyboardButton(text="PAUSE / RESUME", callback_data="help_callback hb1|music"),
            ],
            [
                InlineKeyboardButton(text="SKIP", callback_data="help_callback hb1|music"),
                InlineKeyboardButton(text="STOP / END", callback_data="help_callback hb1|music"),
            ],
            [
                InlineKeyboardButton(text="SEEK", callback_data="help_callback hb13|music"),
                InlineKeyboardButton(text="SPEED", callback_data="help_callback hb15|music"),
                InlineKeyboardButton(text="LOOP", callback_data="help_callback hb8|music"),
            ],
            [
                InlineKeyboardButton(text="QUEUE", callback_data="help_callback hb12|music"),
                InlineKeyboardButton(text="SHUFFLE", callback_data="help_callback hb12|music"),
            ],
            [
                InlineKeyboardButton(text="DOWNLOAD", callback_data="help_callback hb14|music"),
                InlineKeyboardButton(text="LYRICS", callback_data="help_callback hb17|music"),
            ],
            [
                InlineKeyboardButton(text="FILTERS", callback_data="help_callback hb19|music"),
                InlineKeyboardButton(text="AUTOPLAY", callback_data="help_callback hb21|music"),
            ],
            [
                InlineKeyboardButton(text="RADIO", callback_data="help_callback hb22|music"),
                InlineKeyboardButton(text="REELS", callback_data="help_callback hb26|music"),
            ],
            [
                InlineKeyboardButton(text="VIP INTRO", callback_data="help_callback hb24|music"),
                InlineKeyboardButton(text="VC TOOLS", callback_data="help_callback hb20|music"),
            ],
            [
                InlineKeyboardButton(text="BACK", callback_data="help_main"),
                InlineKeyboardButton(text="CLOSE", callback_data="close"),
            ],
        ]
    )


def help_extra_markup(_):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ADMIN", callback_data="help_callback hb1|extra"),
                InlineKeyboardButton(text="AUTH", callback_data="help_callback hb2|extra"),
            ],
            [
                InlineKeyboardButton(text="BROADCAST", callback_data="help_callback hb3|extra"),
                InlineKeyboardButton(text="G-BAN", callback_data="help_callback hb7|extra"),
            ],
            [
                InlineKeyboardButton(text="BL-CHAT", callback_data="help_callback hb4|extra"),
                InlineKeyboardButton(text="BL-USER", callback_data="help_callback hb5|extra"),
            ],
            [
                InlineKeyboardButton(text="C-PLAY", callback_data="help_callback hb6|extra"),
                InlineKeyboardButton(text="MAINTENANCE", callback_data="help_callback hb9|extra"),
            ],
            [
                InlineKeyboardButton(text="PING", callback_data="help_callback hb10|extra"),
                InlineKeyboardButton(text="AI TOOLS", callback_data="help_callback hb16|extra"),
            ],
            [
                InlineKeyboardButton(text="SONG QUIZ", callback_data="help_callback hb23|extra"),
                InlineKeyboardButton(text="SHAZAM", callback_data="help_callback hb25|extra"),
            ],
            [
                InlineKeyboardButton(text="SLEEP TIMER", callback_data="help_callback hb27|extra"),
                InlineKeyboardButton(text="FUN & EXTRA", callback_data="help_callback hb18|extra"),
            ],
            [
                InlineKeyboardButton(text="BACK", callback_data="help_main"),
                InlineKeyboardButton(text="CLOSE", callback_data="close"),
            ],
        ]
    )


def help_back_markup(category="music"):
    target = "help_cat_music" if category == "music" else "help_cat_extra"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="BACK", callback_data=target),
                InlineKeyboardButton(text="MAIN HELP", callback_data="help_main"),
            ],
            [
                InlineKeyboardButton(text="CLOSE", callback_data="close"),
            ]
        ]
    )


def private_help_panel(_):
    return [
        [
            InlineKeyboardButton(
                text="OPEN HELP MENU",
                url=f"https://t.me/{app.username}?start=help",
            )
        ]
    ]
