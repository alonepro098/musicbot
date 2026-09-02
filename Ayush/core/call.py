import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import (
    AlreadyJoinedError,
    NoActiveGroupCall,
    TelegramServerError,
)
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded

import config
from Ayush import LOGGER, YouTube, app
from Ayush.misc import db
from Ayush.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    is_autoplay,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)

from Ayush.utils.exceptions import AssistantErr
from Ayush.utils.formatters import check_duration, seconds_to_min, speed_converter
from Ayush.utils.inline.play import stream_markup
from Ayush.utils.stream.autoclear import auto_clean
from Ayush.utils.thumbnails import get_thumb
from strings import get_string

autoend = {}
counter = {}


async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


AUTOPLAY_HISTORY = {}

GENRE_DATABASE = {
    "sad": {
        "keywords": [
            "tum hi ho", "channa mereya", "agar tum saath ho", "hamari adhuri kahani", "bekhayali",
            "tera chehra", "tujhe bhula diya", "judai", "bewafa", "dard", "sad", "alone",
            "broken", "heartbreak", "emotional", "crying", "rona", "yaad", "tanhai", "bhula dena",
            "kabira", "mana ki hum yaar nahi", "lo maan liya", "hasi ban gaye", "phir bhi tumko chaahunga",
            "khairiyat", "kaash", "ae dil hai mushkil", "main dhoondne ko", "tera zikr", "alvida",
            "bhula na sako ge", "dua", "judaai", "jag ghoomeya", "dil de diya hai", "thodi jagah",
            "pachtaoge", "filhall", "lut gaye", "qismat", "bedardi se pyaar ka", "dil galti kar baitha",
            "mile ho tum humko", "muskurane", "sunn raha hai", "mat aazma re", "saaware", "dil tod ke"
        ],
        "artists": ["arijit singh", "atif aslam", "b praak", "jaani", "armaan malik", "mohit chauhan", "mustafa zahid", "kk"],
        "queries": [
            "top hindi sad songs jukebox",
            "arijit singh emotional heartbreak songs",
            "bollywood sad love songs playlist",
            "atif aslam sad songs collection",
            "best bollywood crying emotional hits",
            "sad romantic hindi songs mix"
        ]
    },
    "romantic": {
        "keywords": [
            "wajah tum ho", "kesariya", "raataan lambiyan", "tum se hi", "pehli nazar",
            "dil diya gallan", "tera ban jaunga", "apna bana le", "o maahi", "satranga",
            "samjhawan", "ishq", "pyaar", "love", "romantic", "mohabbat", "humsafar", "dilbar",
            "khuda jaane", "tera hone laga hoon", "peeloon", "tum jo aaye", "jeene laga hoon",
            "bol do na zara", "sanware", "heeriye", "ve kamleya", "pal", "suno na sangemarmar",
            "kaun tujhe", "dheere dheere", "subhanallah", "mast magan", "nazm nazm", "hawayein",
            "dil sambhal ja zara", "raabta", "gerua", "janib", "soch na sake", "dil jhoom", "pehle bhi main"
        ],
        "artists": ["arijit singh", "jubin nautiyal", "shreya ghoshal", "darshan raval", "neha kakkar", "stebin ben", "vishal mishra"],
        "queries": [
            "bollywood romantic love songs jukebox",
            "latest hindi romantic songs playlist",
            "jubin nautiyal love hits",
            "best romantic love songs collection",
            "arijit singh romantic hits mix",
            "sweet acoustic love songs hindi"
        ]
    },
    "party": {
        "keywords": [
            "abhi toh party shuru hui hai", "kala chashma", "kar gayi chull", "garmi", "badtameez dil",
            "sheila ki jawani", "munni badnam", "hookah bar", "dj", "party", "dance", "club",
            "bhangra", "sharab", "alcohol", "nach", "thumka", "daru", "remix", "mashup",
            "gaddi red thriller", "coca cola", "makhna", "lut gaye remix", "sauda khara khara",
            "hauli hauli", "chote chote peg", "dil chori", "bom diggy", "gallan kardi", "buzz",
            "swag se swagat", "high rated gabru", "lahore", "proper patola", "coka", "tauba tauba",
            "aankh marey", "morni banke", "ghungroo", "nashe si chadh gayi", "dilliwali girlfriend"
        ],
        "artists": ["yo yo honey singh", "badshah", "guru randhawa", "mika singh", "tony kakkar", "hardy sandhu", "raftaar"],
        "queries": [
            "bollywood party dance hits jukebox",
            "punjabi club party bangers",
            "latest hindi dance songs playlist",
            "honey singh badshah party hits",
            "club dj mashup dance songs bollywood",
            "wedding dance party songs hindi"
        ]
    },
    "punjabi": {
        "keywords": [
            "sidhu", "moosewala", "karan aujla", "shubh", "ap dhillon", "diljit", "jatt", "yaar",
            "gabru", "punjabi", "chandigarh", "brampton", "cheques", "winning speech", "brown munde",
            "excuses", "elevated", "white brown black", "softly", "goat", "295", "levels", "so high",
            "never fold", "legend", "same beef", "old skool", "chitta kurta", "mexico", "sheesha",
            "admire you", "tauba tauba", "hass hass", "kinni kinni", "with you", "jee ni karda"
        ],
        "artists": ["sidhu moosewala", "karan aujla", "diljit dosanjh", "ap dhillon", "shubh", "amrit maan", "jordan sandhu"],
        "queries": [
            "punjabi top hits karan aujla sidhu moosewala",
            "latest punjabi hype bangers playlist",
            "shubh ap dhillon vibe songs",
            "diljit dosanjh hit songs collection",
            "trending punjabi car songs"
        ]
    },
    "lofi": {
        "keywords": ["lofi", "slowed", "reverb", "chill", "midnight", "aesthetic", "relax", "sleep", "study", "beats", "peaceful", "night"],
        "artists": ["lofi", "chill", "aesthetic", "vibe"],
        "queries": [
            "hindi lofi aesthetic chill mix",
            "midnight bollywood slowed reverb songs",
            "hindi lofi songs to sleep study",
            "aesthetic peaceful hindi songs"
        ]
    },
    "devotional": {
        "keywords": ["bhajan", "aarti", "chalisa", "krishna", "ram", "shiva", "hanuman", "mata", "radha", "shyam", "mahadev", "ganesh", "devotional", "bhakti"],
        "artists": ["anup jalota", "gulshan kumar", "anuradha paudwal", "jubin nautiyal bhakti", "lakhbir singh lakha", "hansraj raghuwanshi"],
        "queries": [
            "top hindi devotional bhajans",
            "mahadev shiv devotional songs",
            "krishna bhajan peaceful collection",
            "hanuman chalisa bhajans jukebox"
        ]
    },
    "retro": {
        "keywords": ["90s", "80s", "70s", "retro", "old", "evergreen", "classic", "kishore kumar", "lata mangeshkar", "mohd rafi", "mukesh", "rd burman", "kumar sanu", "alka yagnik", "udit narayan"],
        "artists": ["kumar sanu", "alka yagnik", "udit narayan", "kishore kumar", "lata mangeshkar", "mohammad rafi", "asha bhosle", "rd burman"],
        "queries": [
            "90s bollywood evergreen hits jukebox",
            "kumar sanu alka yagnik udit narayan hits",
            "golden 70s 80s kishore kumar romantic songs",
            "evergreen classic old hindi songs"
        ]
    }
}


def _clean_autoplay_title(title: str) -> str:
    import re
    t = re.sub(r"\(.*?\)|\[.*?\]", "", title)
    t = re.sub(r"(?i)\b(official|video|audio|lyrical|song|full video|hd|4k|remix|slowed|reverb|teaser|trailer|status)\b", "", t)
    return " ".join(t.split()).strip()


def _detect_song_genre(title: str) -> str:
    t_lower = title.lower()
    
    # Check specific keyword match
    for genre, data in GENRE_DATABASE.items():
        for kw in data["keywords"]:
            if kw in t_lower:
                return genre

    # Check artist match
    for genre, data in GENRE_DATABASE.items():
        for art in data["artists"]:
            if art in t_lower:
                return genre

    return "romantic"  # default mood


async def _get_smart_autoplay_track(chat_id: int, popped: dict):
    from py_yt import VideosSearch
    import random

    if chat_id not in AUTOPLAY_HISTORY:
        AUTOPLAY_HISTORY[chat_id] = set()

    last_vid = popped.get("vidid")
    if last_vid:
        AUTOPLAY_HISTORY[chat_id].add(str(last_vid))

    raw_title = popped.get("title", "")
    clean_title = _clean_autoplay_title(raw_title)

    detected_genre = _detect_song_genre(raw_title)
    genre_info = GENRE_DATABASE.get(detected_genre, GENRE_DATABASE["romantic"])

    queries = list(genre_info["queries"])
    if clean_title:
        queries.insert(0, f"{clean_title} similar genre songs")
    random.shuffle(queries)

    chosen = None
    for q in queries:
        try:
            results = VideosSearch(q, limit=15)
            res = await results.next()
            items = res.get("result", []) if res else []
            candidates = []
            for item in items:
                v_id = item.get("id")
                v_title = item.get("title", "")
                if not v_id:
                    continue
                if str(v_id) in AUTOPLAY_HISTORY[chat_id]:
                    continue
                c_item_title = _clean_autoplay_title(v_title)
                # Avoid exact same song repetition
                if clean_title and (clean_title.lower() in c_item_title.lower() or c_item_title.lower() in clean_title.lower()):
                    continue
                dur = item.get("duration", "")
                if dur and len(dur.split(":")) > 2:  # skip long compilations > 1 hour
                    continue
                candidates.append(item)

            if candidates:
                chosen = random.choice(candidates[:6])
                break
        except Exception:
            continue

    if not chosen:
        fallback_queries = ["trending bollywood romantic songs", "punjabi hit songs", "lofi chill songs"]
        try:
            results = VideosSearch(random.choice(fallback_queries), limit=10)
            res = await results.next()
            items = res.get("result", []) if res else []
            for item in items:
                v_id = item.get("id")
                if v_id and str(v_id) not in AUTOPLAY_HISTORY[chat_id]:
                    chosen = item
                    break
        except Exception:
            pass

    if chosen:
        AUTOPLAY_HISTORY[chat_id].add(str(chosen.get("id")))
        if len(AUTOPLAY_HISTORY[chat_id]) > 60:
            AUTOPLAY_HISTORY[chat_id].pop()
        return chosen
    return None



class Call:
    def __init__(self):
        self.userbot1 = Client(
            name="AyushAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=100,
        )
        self.userbot2 = Client(
            name="AyushAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(
            self.userbot2,
            cache_duration=100,
        )
        self.userbot3 = Client(
            name="AyushAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(
            self.userbot3,
            cache_duration=100,
        )
        self.userbot4 = Client(
            name="AyushAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(
            self.userbot4,
            cache_duration=100,
        )
        self.userbot5 = Client(
            name="AyushAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(
            self.userbot5,
            cache_duration=100,
        )

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1:
                await self.one.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING2:
                await self.two.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING3:
                await self.three.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING4:
                await self.four.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING5:
                await self.five.leave_group_call(chat_id)
        except:
            pass
        try:
            await _clear_(chat_id)
        except:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != str("1.0"):
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                if str(speed) == str("0.5"):
                    vs = 2.0
                if str(speed) == str("0.75"):
                    vs = 1.35
                if str(speed) == str("1.5"):
                    vs = 0.68
                if str(speed) == str("2.0"):
                    vs = 0.5
                proc = await asyncio.create_subprocess_shell(
                    cmd=(
                        "ffmpeg "
                        "-i "
                        f"{file_path} "
                        "-filter:v "
                        f"setpts={vs}*PTS "
                        "-filter:a "
                        f"atempo={speed} "
                        f"{out}"
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
            else:
                pass
        else:
            out = file_path
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        stream = (
            AudioVideoPiped(
                out,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
                additional_ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
            if playing[0]["streamtype"] == "video"
            else AudioPiped(
                out,
                audio_parameters=HighQualityAudio(),
                additional_ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
        )
        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.change_stream(chat_id, stream)
        else:
            raise AssistantErr("Umm")
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        if video:
            stream = AudioVideoPiped(
                link,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
            )
        else:
            stream = AudioPiped(link, audio_parameters=HighQualityAudio())
        await assistant.change_stream(
            chat_id,
            stream,
        )

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        stream = (
            AudioVideoPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
            if mode == "video"
            else AudioPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        )
        await assistant.change_stream(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        await assistant.join_group_call(
            config.LOGGER_ID,
            AudioVideoPiped(link),
            stream_type=StreamType().pulse_stream,
        )
        await asyncio.sleep(0.2)
        await assistant.leave_group_call(config.LOGGER_ID)

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        if video:
            stream = AudioVideoPiped(
                link,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
            )
        else:
            stream = (
                AudioVideoPiped(
                    link,
                    audio_parameters=HighQualityAudio(),
                    video_parameters=MediumQualityVideo(),
                )
                if video
                else AudioPiped(link, audio_parameters=HighQualityAudio())
            )
        try:
            await assistant.join_group_call(
                chat_id,
                stream,
                stream_type=StreamType().pulse_stream,
            )
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except AlreadyJoinedError:
            raise AssistantErr(_["call_9"])
        except TelegramServerError:
            raise AssistantErr(_["call_10"])
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            await auto_clean(popped)
            if not check:
                if await is_autoplay(chat_id) and popped:
                    try:
                        chosen = await _get_smart_autoplay_track(chat_id, popped)
                        if chosen:
                            vidid = chosen.get("id")
                            rel_title = chosen.get("title", "AutoPlay Music")
                            duration_min = chosen.get("duration", "3:30")
                            from Ayush.utils.formatters import time_to_seconds
                            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
                            orig_chat = popped.get("chat_id", chat_id)

                            db[chat_id] = [{
                                "title": rel_title,
                                "dur": duration_min,
                                "streamtype": "audio",
                                "by": "⚡ ᴀᴜᴛᴏ-ᴘʟᴀʏ ᴀɪ",
                                "chat_id": orig_chat,
                                "file": f"vid_{vidid}",
                                "vidid": vidid,
                                "seconds": duration_sec,
                                "played": 0,
                            }]
                            check = db.get(chat_id)
                    except Exception:
                        pass

                if not check:
                    await _clear_(chat_id)
                    return await client.leave_group_call(chat_id)
        except:

            try:
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)
            except:
                return

        else:
            queued = check[0]["file"]
            language = await get_lang(chat_id)
            _ = get_string(language)
            title = (check[0]["title"]).title()
            user = check[0]["by"]
            original_chat_id = check[0]["chat_id"]
            streamtype = check[0]["streamtype"]
            videoid = check[0]["vidid"]
            db[chat_id][0]["played"] = 0
            exis = (check[0]).get("old_dur")
            if exis:
                db[chat_id][0]["dur"] = exis
                db[chat_id][0]["seconds"] = check[0]["old_second"]
                db[chat_id][0]["speed_path"] = None
                db[chat_id][0]["speed"] = 1.0
            video = True if str(streamtype) == "video" else False
            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                if video:
                    stream = AudioVideoPiped(
                        link,
                        audio_parameters=HighQualityAudio(),
                        video_parameters=MediumQualityVideo(),
                    )
                else:
                    stream = AudioPiped(
                        link,
                        audio_parameters=HighQualityAudio(),
                    )
                try:
                    await client.change_stream(chat_id, stream)
                except Exception:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif "vid_" in queued:
                mystic = await app.send_message(original_chat_id, _["call_7"])
                try:
                    file_path, direct = await YouTube.download(
                        videoid,
                        mystic,
                        videoid=True,
                        video=True if str(streamtype) == "video" else False,
                    )
                except:
                    return await mystic.edit_text(
                        _["call_6"], disable_web_page_preview=True
                    )
                if video:
                    stream = AudioVideoPiped(
                        file_path,
                        audio_parameters=HighQualityAudio(),
                        video_parameters=MediumQualityVideo(),
                    )
                else:
                    stream = AudioPiped(
                        file_path,
                        audio_parameters=HighQualityAudio(),
                    )
                try:
                    await client.change_stream(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                await mystic.delete()
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            elif "index_" in queued:
                stream = (
                    AudioVideoPiped(
                        videoid,
                        audio_parameters=HighQualityAudio(),
                        video_parameters=MediumQualityVideo(),
                    )
                    if str(streamtype) == "video"
                    else AudioPiped(videoid, audio_parameters=HighQualityAudio())
                )
                try:
                    await client.change_stream(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    caption=_["stream_2"].format(user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                if video:
                    stream = AudioVideoPiped(
                        queued,
                        audio_parameters=HighQualityAudio(),
                        video_parameters=MediumQualityVideo(),
                    )
                else:
                    stream = AudioPiped(
                        queued,
                        audio_parameters=HighQualityAudio(),
                    )
                try:
                    await client.change_stream(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                if videoid == "telegram":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.TELEGRAM_AUDIO_URL
                        if str(streamtype) == "audio"
                        else config.TELEGRAM_VIDEO_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                elif videoid == "soundcloud":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.SOUNCLOUD_IMG_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                else:
                    img = await get_thumb(videoid)
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=img,
                        caption=_["stream_1"].format(
                            f"https://t.me/{app.username}?start=info_{videoid}",
                            title[:23],
                            check[0]["dur"],
                            user,
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"

    async def ping(self):
        pings = []
        if config.STRING1:
            pings.append(await self.one.ping)
        if config.STRING2:
            pings.append(await self.two.ping)
        if config.STRING3:
            pings.append(await self.three.ping)
        if config.STRING4:
            pings.append(await self.four.ping)
        if config.STRING5:
            pings.append(await self.five.ping)
        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        if config.STRING1:
            await self.one.start()
        if config.STRING2:
            await self.two.start()
        if config.STRING3:
            await self.three.start()
        if config.STRING4:
            await self.four.start()
        if config.STRING5:
            await self.five.start()

    async def decorators(self):
        @self.one.on_kicked()
        @self.two.on_kicked()
        @self.three.on_kicked()
        @self.four.on_kicked()
        @self.five.on_kicked()
        @self.one.on_closed_voice_chat()
        @self.two.on_closed_voice_chat()
        @self.three.on_closed_voice_chat()
        @self.four.on_closed_voice_chat()
        @self.five.on_closed_voice_chat()
        @self.one.on_left()
        @self.two.on_left()
        @self.three.on_left()
        @self.four.on_left()
        @self.five.on_left()
        async def stream_services_handler(_, chat_id: int):
            await self.stop_stream(chat_id)

        @self.one.on_stream_end()
        @self.two.on_stream_end()
        @self.three.on_stream_end()
        @self.four.on_stream_end()
        @self.five.on_stream_end()
        async def stream_end_handler1(client, update: Update):
            if not isinstance(update, StreamAudioEnded):
                return
            await self.change_stream(client, update.chat_id)


Aayu = Call()
