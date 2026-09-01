from typing import Union
from pyrogram.types import InlineKeyboardButton


def setting_markup(_):
    buttons = [
        [
            InlineKeyboardButton(text="ᴀᴜᴛʜ ᴜsᴇʀs", callback_data="AU"),
            InlineKeyboardButton(text="ʟᴀɴɢᴜᴀɢᴇ", callback_data="LG"),
        ],
        [
            InlineKeyboardButton(text="ᴘʟᴀʏ ᴍᴏᴅᴇ", callback_data="PM"),
            InlineKeyboardButton(text="ᴠᴏᴛɪɴɢ ᴍᴏᴅᴇ", callback_data="VM"),
        ],
        [
            InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="settingsback_helper"),
            InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close"),
        ],
    ]
    return buttons


def vote_mode_markup(_, current, mode: Union[bool, str] = None):
    status_text = "ᴏɴ" if mode == True else "ᴏғғ"
    buttons = [
        [
            InlineKeyboardButton(text="ᴠᴏᴛɪɴɢ ᴍᴏᴅᴇ ➜", callback_data="VOTEANSWER"),
            InlineKeyboardButton(
                text=status_text,
                callback_data="VOMODECHANGE",
            ),
        ],
        [
            InlineKeyboardButton(text="➖ 2", callback_data="FERRARIUDTI M"),
            InlineKeyboardButton(
                text=f"ᴄᴜʀʀᴇɴᴛ : {current}",
                callback_data="ANSWERVOMODE",
            ),
            InlineKeyboardButton(text="➕ 2", callback_data="FERRARIUDTI A"),
        ],
        [
            InlineKeyboardButton(
                text="ʙᴀᴄᴋ",
                callback_data="settings_helper",
            ),
            InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close"),
        ],
    ]
    return buttons


def auth_users_markup(_, status: Union[bool, str] = None):
    status_text = "ᴀᴅᴍɪɴs" if status == True else "ᴇᴠᴇʀʏᴏɴᴇ"
    buttons = [
        [
            InlineKeyboardButton(text="ᴀᴜᴛʜ ᴜsᴇʀs ➜", callback_data="AUTHANSWER"),
            InlineKeyboardButton(
                text=status_text,
                callback_data="AUTH",
            ),
        ],
        [
            InlineKeyboardButton(text="ᴀᴜᴛʜ ᴜsᴇʀs ʟɪsᴛ", callback_data="AUTHLIST"),
        ],
        [
            InlineKeyboardButton(
                text="ʙᴀᴄᴋ",
                callback_data="settings_helper",
            ),
            InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close"),
        ],
    ]
    return buttons


def playmode_users_markup(
    _,
    Direct: Union[bool, str] = None,
    Group: Union[bool, str] = None,
    Playtype: Union[bool, str] = None,
):
    search_text = "ᴅɪʀᴇᴄᴛ" if Direct == True else "ɪɴʟɪɴᴇ"
    channel_text = "ᴀᴅᴍɪɴs" if Group == True else "ᴇᴠᴇʀʏᴏɴᴇ"
    play_text = "ᴀᴅᴍɪɴs" if Playtype == True else "ᴇᴠᴇʀʏᴏɴᴇ"

    buttons = [
        [
            InlineKeyboardButton(text="sᴇᴀʀᴄʜ ᴍᴏᴅᴇ ➜", callback_data="SEARCHANSWER"),
            InlineKeyboardButton(
                text=search_text,
                callback_data="MODECHANGE",
            ),
        ],
        [
            InlineKeyboardButton(text="ᴄ-ᴘʟᴀʏ ᴍᴏᴅᴇ ➜", callback_data="AUTHANSWER"),
            InlineKeyboardButton(
                text=channel_text,
                callback_data="CHANNELMODECHANGE",
            ),
        ],
        [
            InlineKeyboardButton(text="ᴘʟᴀʏ ᴛʏᴘᴇ ➜", callback_data="PLAYTYPEANSWER"),
            InlineKeyboardButton(
                text=play_text,
                callback_data="PLAYTYPECHANGE",
            ),
        ],
        [
            InlineKeyboardButton(
                text="ʙᴀᴄᴋ",
                callback_data="settings_helper",
            ),
            InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close"),
        ],
    ]
    return buttons
