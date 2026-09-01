from typing import Union
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, Message

from Ayush import app
from Ayush.utils.database import get_lang
from Ayush.utils.decorators.language import LanguageStart, languageCB
from Ayush.utils.inline.help import (
    help_main_markup,
    help_music_markup,
    help_extra_markup,
    help_back_markup,
    private_help_panel,
)
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers


HELP_TEXT_MAP = {
    "hb1": helpers.HELP_1,
    "hb2": helpers.HELP_2,
    "hb3": helpers.HELP_3,
    "hb4": helpers.HELP_4,
    "hb5": helpers.HELP_5,
    "hb6": helpers.HELP_6,
    "hb7": helpers.HELP_7,
    "hb8": helpers.HELP_8,
    "hb9": helpers.HELP_9,
    "hb10": helpers.HELP_10,
    "hb11": helpers.HELP_11,
    "hb12": helpers.HELP_12,
    "hb13": helpers.HELP_13,
    "hb14": helpers.HELP_14,
    "hb15": helpers.HELP_15,
    "hb16": helpers.HELP_16,
    "hb17": helpers.HELP_17,
    "hb18": helpers.HELP_18,
    "hb19": helpers.HELP_19,
    "hb20": helpers.HELP_20,
    "hb21": helpers.HELP_21,
    "hb22": helpers.HELP_22,
    "hb23": helpers.HELP_23,
    "hb24": helpers.HELP_24,
    "hb25": helpers.HELP_25,
    "hb26": helpers.HELP_26,
    "hb27": helpers.HELP_27,
}


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex(r"^(settings_back_helper|help_main)$") & ~BANNED_USERS)
async def helper_private(client: app, update: Union[types.Message, types.CallbackQuery]):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except Exception:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = help_main_markup(_)
        await update.edit_message_text(
            "<blockquote><b><u>COMMANDS & FEATURES MENU</u></b>\n\nChoose a category below to explore available commands:</blockquote>",
            reply_markup=keyboard,
        )
    else:
        try:
            await update.delete()
        except Exception:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = help_main_markup(_)
        await update.reply_photo(
            photo=START_IMG_URL,
            caption="<blockquote><b><u>COMMANDS & FEATURES MENU</u></b>\n\nChoose a category below to explore available commands:</blockquote>",
            reply_markup=keyboard,
        )


@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))


@app.on_callback_query(filters.regex(r"^help_cat_music$") & ~BANNED_USERS)
@languageCB
async def help_music_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    keyboard = help_music_markup(_)
    await CallbackQuery.edit_message_text(
        "<blockquote>🎵 <b><u>MUSIC COMMANDS</u></b>\n\nSelect any music feature below to view its usage:</blockquote>",
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex(r"^help_cat_extra$") & ~BANNED_USERS)
@languageCB
async def help_extra_cb(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except Exception:
        pass
    keyboard = help_extra_markup(_)
    await CallbackQuery.edit_message_text(
        "<blockquote>🛠️ <b><u>EXTRA & MANAGEMENT COMMANDS</u></b>\n\nSelect any feature below to view its usage:</blockquote>",
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex(r"^help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    payload = callback_data.split(None, 1)[1]
    
    if "|" in payload:
        cb_code, category = payload.split("|", 1)
    else:
        cb_code = payload
        category = "music"

    help_content = HELP_TEXT_MAP.get(cb_code, "<blockquote>No help available for this topic.</blockquote>")
    keyboard = help_back_markup(category)
    await CallbackQuery.edit_message_text(help_content, reply_markup=keyboard)
