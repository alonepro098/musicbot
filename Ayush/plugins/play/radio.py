import logging

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import BANNED_USERS, adminlist
from strings import get_string
from Ayush import app
from Ayush.misc import SUDOERS
from Ayush.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
)
from Ayush.utils.logger import play_logs
from Ayush.utils.stream.stream import stream

RADIO_STATION = {
    "Air Bilaspur": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio110/playlist.m3u8",
    "Air Raipur": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio118/playlist.m3u8",
    "Capital FM": "http://media-ice.musicradio.com/CapitalMP3?.mp3&listening-from-radio-garden=1616312105154",
    "English": "https://hls-01-regions.emgsound.ru/11_msk/playlist.m3u8",
    "Mirchi": "http://peridot.streamguys.com:7150/Mirchi",
    "Bollywood Love": "https://nl4.mystreaming.net/uber/bollywoodlove/icecast.audio",
    "Radio Today": "http://stream.zenolive.com/8wv4d8g4344tv",
    "Bollywood": "https://stream-159.zeno.fm/143d7gty24zuv?zt=eyJhbGciOiJIUzI1NiJ9.eyJzdHJlYW0iOiIxNDNkN2d0eTI0enV2IiwiaG9zdCI6InN0cmVhbS0xNTkuemVuby5mbSIsInJ0dGwiOjUsImp0aSI6ImgybmNNdkhiVGZpYkE2MGQ4U3MxVGciLCJpYXQiOjE3MjgwMTkwOTEsImV4cCI6MTcyODAxOTE1MX0.0gd1Nx6ke2cXJR1pJxxFsVTKHmtQ3OZnkRh_fKFoRUA",
    "YouTube": "https://www.youtube.com/live/eu191hR_LEc?si=T-9QYD548jd0Mogp",
    "Zee News": "https://www.youtube.com/live/TPcmrPrygDc?si=hiHBkIidgurQAd1P",
    "Aaj Tak": "https://www.youtube.com/live/Nq2wYlWFucg?si=usY4UYiSBInKA0S1",
}

valid_stations = "\n".join([f"`{name}`" for name in sorted(RADIO_STATION.keys())])


@app.on_message(
    filters.command(["radioplayforce", "radio", "cradio"])
    & filters.group
    & ~BANNED_USERS
)
async def radio(client, message: Message):
    msg = await message.reply_text("ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ....")
    try:
        try:
            userbot = await get_assistant(message.chat.id)
            get = await app.get_chat_member(message.chat.id, userbot.id)
        except ChatAdminRequired:
            return await msg.edit_text(
                f"» ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ғᴏʀ ɪɴᴠɪᴛɪɴɢ {userbot.mention} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}."
            )
        if get.status == ChatMemberStatus.BANNED:
            return await msg.edit_text(
                text=f"» {userbot.mention} ᴀssɪsᴛᴀɴᴛ ɪs ʙᴀɴɴᴇᴅ ɪɴ {message.chat.title}\n\n𖢵 ɪᴅ : `{userbot.id}`\n𖢵 ɴᴀᴍᴇ : {userbot.mention}\n𖢵 ᴜsᴇʀɴᴀᴍᴇ : @{userbot.username}\n\nᴘʟᴇᴀsᴇ ᴜɴʙᴀɴ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴀɴᴅ ᴘʟᴀʏ ᴀɢᴀɪɴ...",
            )
    except UserNotParticipant:
        if message.chat.username:
            invitelink = message.chat.username
            try:
                await userbot.resolve_peer(invitelink)
            except Exception as ex:
                logging.exception(ex)
        else:
            try:
                invitelink = await client.export_chat_invite_link(message.chat.id)
            except ChatAdminRequired:
                return await msg.edit_text(
                    f"» ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ғᴏʀ ɪɴᴠɪᴛɪɴɢ {userbot.mention} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}."
                )
            except InviteRequestSent:
                try:
                    await app.approve_chat_join_request(message.chat.id, userbot.id)
                except Exception as e:
                    return await msg.edit(
                        f"ғᴀɪʟᴇᴅ ᴛᴏ ɪɴᴠɪᴛᴇ {userbot.mention} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}.\n\n**ʀᴇᴀsᴏɴ :** `{ex}`"
                    )
            except Exception as ex:
                if "channels.JoinChannel" in str(ex) or "Username not found" in str(ex):
                    return await msg.edit_text(
                        f"» ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ғᴏʀ ɪɴᴠɪᴛɪɴɢ {userbot.mention} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}."
                    )
                else:
                    return await msg.edit_text(
                        f"ғᴀɪʟᴇᴅ ᴛᴏ ɪɴᴠɪᴛᴇ {userbot.mention} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}.\n\n**ʀᴇᴀsᴏɴ :** `{ex}`"
                    )
        if invitelink.startswith("https://t.me/+"):
            invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
        anon = await msg.edit_text(
            f"ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...\n\nɪɴᴠɪᴛɪɴɢ {userbot.mention} ᴛᴏ {message.chat.title}."
        )
        try:
            await userbot.join_chat(invitelink)
            await asyncio.sleep(2)
            await msg.edit_text(
                f"{userbot.mention} ᴊᴏɪɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ,\n\nsᴛᴀʀᴛɪɴɢ sᴛʀᴇᴀᴍ..."
            )
        except UserAlreadyParticipant:
            pass
        except InviteRequestSent:
            try:
                await app.approve_chat_join_request(message.chat.id, userbot.id)
            except Exception as e:
                return await msg.edit(
                    f"ғᴀɪʟᴇᴅ ᴛᴏ ɪɴᴠɪᴛᴇ {userbot.mention} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}.\n\n**ʀᴇᴀsᴏɴ :** `{ex}`"
                )
        except Exception as ex:
            if "channels.JoinChannel" in str(ex) or "Username not found" in str(ex):
                return await msg.edit_text(
                    f"» ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ғᴏʀ ɪɴᴠɪᴛɪɴɢ {userbot.mention} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}."
                )
            else:
                return await msg.edit_text(
                    f"ғᴀɪʟᴇᴅ ᴛᴏ ɪɴᴠɪᴛᴇ {userbot.mention} ᴀssɪsᴛᴀɴᴛ ᴛᴏ {message.chat.title}.\n\n**ʀᴇᴀsᴏɴ :** `{ex}`"
                )

        try:
            await userbot.resolve_peer(invitelink)
        except:
            pass
    await msg.delete()
    station_name = " ".join(message.command[1:])
    RADIO_URL = RADIO_STATION.get(station_name)
    if RADIO_URL:
        language = await get_lang(message.chat.id)
        _ = get_string(language)
        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)
        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    return await message.reply_text(_["admin_18"])
                else:
                    if message.from_user.id not in admins:
                        return await message.reply_text(_["play_4"])
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_12"])
            try:
                chat = await app.get_chat(chat_id)
            except:
                return await message.reply_text(_["cplay_4"])
            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None

        video = None
        mystic = await message.reply_text(
            _["play_2"].format(channel) if channel else _["play_1"]
        )
        try:
            await stream(
                _,
                mystic,
                message.from_user.id,
                RADIO_URL,
                chat_id,
                message.from_user.mention,
                message.chat.id,
                video=video,
                streamtype="index",
            )
        except Exception as e:
            ex_type = type(e).__name__
            err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
            return await mystic.edit_text(err)
        return await play_logs(message, streamtype="M3u8 or Index Link")
    else:
        buttons = [
            [
                InlineKeyboardButton(text="📻 ᴍɪʀᴄʜɪ", callback_data="RADIO_PLAY|Mirchi"),
                InlineKeyboardButton(text="📻 ʙᴏʟʟʏᴡᴏᴏᴅ ʟᴏᴠᴇ", callback_data="RADIO_PLAY|Bollywood Love"),
            ],
            [
                InlineKeyboardButton(text="📻 ᴄᴀᴘɪᴛᴀʟ ғᴍ", callback_data="RADIO_PLAY|Capital FM"),
                InlineKeyboardButton(text="📻 ʙᴏʟʟʏᴡᴏᴏᴅ", callback_data="RADIO_PLAY|Bollywood"),
            ],
            [
                InlineKeyboardButton(text="📻 ʀᴀᴅɪᴏ ᴛᴏᴅᴀʏ", callback_data="RADIO_PLAY|Radio Today"),
                InlineKeyboardButton(text="📻 ᴇɴɢʟɪsʜ", callback_data="RADIO_PLAY|English"),
            ],
            [
                InlineKeyboardButton(text="📺 ᴢᴇᴇ ɴᴇᴡs", callback_data="RADIO_PLAY|Zee News"),
                InlineKeyboardButton(text="📺 ᴀᴀᴊ ᴛᴀᴋ", callback_data="RADIO_PLAY|Aaj Tak"),
            ],
            [
                InlineKeyboardButton(text="📻 ᴀɪʀ ʀᴀɪᴘᴜʀ", callback_data="RADIO_PLAY|Air Raipur"),
                InlineKeyboardButton(text="📻 ᴀɪʀ ʙɪʟᴀsᴘᴜʀ", callback_data="RADIO_PLAY|Air Bilaspur"),
            ],
            [
                InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
            ],
        ]
        await message.reply_text(
            "<blockquote>📻 <b><u>ʟɪᴠᴇ ʀᴀᴅɪᴏ & ɴᴇᴡs sᴛᴀᴛɪᴏɴs</u></b>\n\n"
            "✨ <i>ᴄʟɪᴄᴋ ᴀɴʏ sᴛᴀᴛɪᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɪɴsᴛᴀɴᴛʟʏ sᴛʀᴇᴀᴍ ʟɪᴠᴇ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ :</i>\n\n"
            f"{valid_stations}</blockquote>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


@app.on_callback_query(filters.regex(r"^RADIO_PLAY\|") & ~BANNED_USERS)
async def radio_callback_stream(client, CallbackQuery):
    station_name = CallbackQuery.data.split("|")[1]
    RADIO_URL = RADIO_STATION.get(station_name)
    if not RADIO_URL:
        return await CallbackQuery.answer("❌ Station not found!", show_alert=True)

    chat_id = CallbackQuery.message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)

    mystic = await CallbackQuery.message.reply_text(f"<blockquote>📻 <b>sᴛᴀʀᴛɪɴɢ ʟɪᴠᴇ sᴛʀᴇᴀᴍ ғᴏʀ {station_name}...</b></blockquote>")
    try:
        await stream(
            _,
            mystic,
            CallbackQuery.from_user.id,
            RADIO_URL,
            chat_id,
            CallbackQuery.from_user.mention,
            chat_id,
            video=None,
            streamtype="index",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
        return await mystic.edit_text(err)

    await CallbackQuery.answer(f"▶️ Playing {station_name}")


__MODULE__ = "Rᴀᴅɪᴏ"
__HELP__ = f"<blockquote><b>📻 <u>ʟɪᴠᴇ ʀᴀᴅɪᴏ & ɴᴇᴡs sᴛᴀᴛɪᴏɴs</u></b>\n\n/radio [station name] : ᴘʟᴀʏ ʟɪᴠᴇ ʀᴀᴅɪᴏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.\n/cradio [station name] : ᴘʟᴀʏ ʟɪᴠᴇ ʀᴀᴅɪᴏ ɪɴ ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ.\n\n<b><u>ᴀᴠᴀɪʟᴀʙʟᴇ sᴛᴀᴛɪᴏɴs:</u></b>\n{valid_stations}</blockquote>"

