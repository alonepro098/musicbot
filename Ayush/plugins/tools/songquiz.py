import os
import random
import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from py_yt import VideosSearch
import yt_dlp

from Ayush import app
from Ayush.core.call import Aayu
from Ayush.utils.database import get_lang, is_active_chat, group_assistant
from strings import get_string
from config import BANNED_USERS

# ==========================================
# 🎵 QUIZ SONGS LIST (ADD / EDIT SONGS HERE)
# ==========================================
QUIZ_SONG_LIST = [
    "Tum Hi Ho Aashiqui 2",
    "Kesariya Brahmastra",
    "Wajah Tum Ho Hate Story 3",
    "Abhi Toh Party Shuru Hui Hai Khoobsurat",
    "Channa Mereya Ae Dil Hai Mushkil",
    "Agar Tum Saath Ho Tamasha",
    "Kala Chashma Baar Baar Dekho",
    "Bekhayali Kabir Singh",
    "Apna Bana Le Bhediya",
    "Tere Vaaste Zara Hatke Zara Bachke",
    "Dil Diyan Gallan Tiger Zinda Hai",
    "Lut Gaye Jubin Nautiyal",
    "Jeene Laga Hoon Ramaiya Vastavaiya",
    "Kaun Tujhe MS Dhoni",
    "Raataan Lambiyan Shershaah",
    "Pee Loon Once Upon A Time In Mumbaai",
    "Tu Jaane Na Ajab Prem Ki Ghazab Kahani",
    "Badtameez Dil Yeh Jawaani Hai Deewani",
    "Ghungroo War",
    "Nashe Si Chadh Gayi Befikre",
    "Kar Gayi Chull Kapoor and Sons",
    "Chaleya Jawan",
    "O Maahi Dunki",
    "Satranga Animal",
    "Samjhawan Humpty Sharma Ki Dulhania",
    "Heeriye Arijit Singh Jasleen Royal",
    "Winning Speech Karan Aujla",
    "295 Sidhu Moosewala",
    "Cheques Shubh",
    "Brown Munde AP Dhillon",
    "Excuses AP Dhillon",
    "Tauba Tauba Bad Newz",
    "Zara Sa Jannat",
    "Subhanallah Yeh Jawaani Hai Deewani",
    "Mast Magan 2 States",
    "Hawayein Jab Harry Met Sejal",
    "Dil Sambhal Ja Zara Murder 2",
    "Gerua Dilwale",
    "Soch Na Sake Airlift",
    "Tum Se Hi Jab We Met"
]

ACTIVE_QUIZZES = {}


def _download_5s_clip(link: str, output_path: str):
    os.makedirs("cache", exist_ok=True)
    
    # 1. Fast direct streaming extraction
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            stream_url = info.get("url")
            if stream_url:
                os.system(f'ffmpeg -y -ss 00:00:30 -t 5 -i "{stream_url}" -vn -c:a libmp3lame -b:a 128k "{output_path}"')
                if os.path.exists(output_path) and os.path.getsize(output_path) > 3000:
                    return True
                # Fallback to 00:00:05
                os.system(f'ffmpeg -y -t 5 -i "{stream_url}" -vn -c:a libmp3lame -b:a 128k "{output_path}"')
                if os.path.exists(output_path) and os.path.getsize(output_path) > 3000:
                    return True
    except Exception:
        pass

    # 2. Section download fallback
    try:
        sec_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "download_ranges": yt_dlp.utils.download_range_func(None, [(30, 35)]),
            "force_keyframes_at_cuts": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ],
        }
        with yt_dlp.YoutubeDL(sec_opts) as ydl:
            ydl.download([link])
        if os.path.exists(output_path) and os.path.getsize(output_path) > 3000:
            return True
    except Exception:
        pass

    # 3. Full download & trim fallback
    temp_full = f"cache/temp_{random.randint(1000, 9999)}"
    try:
        full_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{temp_full}.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ],
        }
        with yt_dlp.YoutubeDL(full_opts) as ydl:
            ydl.download([link])
        
        real_temp = f"{temp_full}.mp3"
        if os.path.exists(real_temp):
            os.system(f'ffmpeg -y -ss 00:00:30 -t 5 -i "{real_temp}" -c:a libmp3lame -b:a 128k "{output_path}"')
            if not os.path.exists(output_path) or os.path.getsize(output_path) < 3000:
                os.system(f'ffmpeg -y -t 5 -i "{real_temp}" -c:a libmp3lame -b:a 128k "{output_path}"')
            try:
                os.remove(real_temp)
            except Exception:
                pass
            if os.path.exists(output_path) and os.path.getsize(output_path) > 3000:
                return True
    except Exception:
        pass

    return os.path.exists(output_path) and os.path.getsize(output_path) > 3000


async def start_vc_quiz(chat_id: int, user_id: int, user_name: str, message: Message = None):
    chosen_query = random.choice(QUIZ_SONG_LIST)
    
    # Search on YT
    results = VideosSearch(chosen_query, limit=1)
    res = await results.next()
    items = res.get("result", [])
    if not items:
        if message:
            return await message.reply_text("❌ <i>Failed to search song on YouTube. Please try again!</i>")
        return

    track = items[0]
    song_title = track["title"]
    song_link = track["link"]
    song_vidid = track["id"]

    quiz_audio_path = f"cache/quiz_{chat_id}_{random.randint(100, 999)}.mp3"

    # Download 5s audio clip in background thread
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(None, _download_5s_clip, song_link, quiz_audio_path)

    if not success or not os.path.exists(quiz_audio_path):
        if message:
            return await message.reply_text("❌ <i>Could not extract 5-second audio snippet. Please try again!</i>")
        return

    ACTIVE_QUIZZES[chat_id] = {
        "title": song_title,
        "link": song_link,
        "vidid": song_vidid,
        "query": chosen_query,
        "revealed": False,
    }

    # Play 5-second tune in VC
    try:
        if await is_active_chat(chat_id):
            assistant = await group_assistant(Aayu, chat_id)
            from pytgcalls.types.input_stream import AudioPiped
            from pytgcalls.types.input_stream.quality import HighQualityAudio
            await assistant.change_stream(chat_id, AudioPiped(quiz_audio_path, audio_parameters=HighQualityAudio()))
        else:
            await Aayu.join_call(chat_id, chat_id, quiz_audio_path, video=None)
    except Exception:
        pass

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="👁️ ʀᴇᴠᴇᴀʟ ᴀɴsᴡᴇʀ", callback_data=f"QUIZ_REVEAL|{chat_id}"),
                InlineKeyboardButton(text="🔄 ɴᴇxᴛ ǫᴜɪᴢ", callback_data=f"QUIZ_NEXT|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
            ]
        ]
    )

    caption = (
        "<blockquote>🎮 <b><u>GUESS THE SONG IN VC!</u></b>\n\n"
        "🔊 <b>5-second music tune is playing in Voice Chat right now!</b>\n"
        "👂 <i>Listen carefully to the tune in VC and guess the song name with your friends in chat!</i>\n\n"
        "⏱️ <i>After everyone has guessed, click <b>'Reveal Answer'</b> below!</i></blockquote>"
    )

    if message:
        await message.reply_text(caption, reply_markup=buttons)

    # Clean 5-second file after 15 seconds
    await asyncio.sleep(15)
    if os.path.exists(quiz_audio_path):
        try:
            os.remove(quiz_audio_path)
        except Exception:
            pass


@app.on_message(filters.command(["songquiz", "musicquiz", "guessthesong"]) & filters.group & ~BANNED_USERS)
async def song_quiz_command(client, message: Message):
    m = await message.reply_text("<blockquote>🎮 <i>Loading 5-second VC song quiz tune... Please wait...</i></blockquote>")
    await start_vc_quiz(message.chat.id, message.from_user.id, message.from_user.first_name, message)
    try:
        await m.delete()
    except Exception:
        pass


@app.on_callback_query(filters.regex(r"^QUIZ_REVEAL\|") & ~BANNED_USERS)
async def quiz_reveal_callback(client, CallbackQuery: CallbackQuery):
    chat_id = int(CallbackQuery.data.split("|")[1])
    if chat_id not in ACTIVE_QUIZZES:
        return await CallbackQuery.answer("⚠️ No active quiz round found!", show_alert=True)

    quiz = ACTIVE_QUIZZES[chat_id]
    quiz["revealed"] = True
    song_name = quiz["title"]

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="▶️ ᴘʟᴀʏ ғᴜʟʟ sᴏɴɢ ɪɴ ᴠᴄ", callback_data=f"CPLAY_SEARCH|{quiz['query']}"),
            ],
            [
                InlineKeyboardButton(text="🔄 ɴᴇxᴛ ǫᴜɪᴢ", callback_data=f"QUIZ_NEXT|{chat_id}"),
                InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
            ]
        ]
    )

    await CallbackQuery.edit_message_text(
        f"<blockquote>🎉 <b><u>SONG QUIZ ANSWER REVEALED!</u></b>\n\n"
        f"🎵 <b>The Song Was :</b> <code>{song_name}</code>\n\n"
        f"✨ <i>Did you guess it right? Click below to stream the full song in VC or play the next quiz!</i></blockquote>",
        reply_markup=buttons,
    )


@app.on_callback_query(filters.regex(r"^QUIZ_NEXT\|") & ~BANNED_USERS)
async def quiz_next_callback(client, CallbackQuery: CallbackQuery):
    chat_id = int(CallbackQuery.data.split("|")[1])
    await CallbackQuery.edit_message_text("<blockquote>🔄 <i>Loading next 5-second VC tune...</i></blockquote>")
    await start_vc_quiz(chat_id, CallbackQuery.from_user.id, CallbackQuery.from_user.first_name, CallbackQuery.message)


@app.on_callback_query(filters.regex(r"^CPLAY_SEARCH\|") & ~BANNED_USERS)
async def cplay_search_callback(client, CallbackQuery: CallbackQuery):
    query = CallbackQuery.data.split("|", 1)[1]
    chat_id = CallbackQuery.message.chat.id
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name

    await CallbackQuery.edit_message_text(f"<blockquote>▶️ <i>Streaming full song: <b>{query}</b> in Voice Chat...</i></blockquote>")

    try:
        from py_yt import VideosSearch
        results = VideosSearch(query, limit=1)
        res = await results.next()
        track = res["result"][0]
        vidid = track["id"]

        language = await get_lang(chat_id)
        _ = get_string(language)

        from Ayush.utils.stream.stream import stream
        await stream(
            _,
            CallbackQuery.message,
            user_id,
            f"https://www.youtube.com/watch?v={vidid}",
            chat_id,
            user_name,
            chat_id,
            video=None,
            streamtype="youtube",
        )
    except Exception as e:
        await CallbackQuery.message.reply_text(f"❌ <i>Error playing full song: {e}</i>")
