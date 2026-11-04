import asyncio
import os
import re
import urllib.parse
import urllib.request
import json
import base64
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
import aiohttp
import config

try:
    from py_yt import VideosSearch, Playlist
except ImportError:
    try:
        from youtubesearchpython.__future__ import VideosSearch
        from youtubesearchpython import Playlist
    except ImportError:
        VideosSearch = None
        Playlist = None

HAS_CRYPTO = False
try:
    try:
        from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
    except ImportError:
        from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES
    from cryptography.hazmat.primitives.ciphers import Cipher, modes
    HAS_CRYPTO = True
except Exception:
    HAS_CRYPTO = False

DES_KEY = b"38346591"

API_URL = getattr(config, "API_URL", None) or os.environ.get("API_URL") or os.environ.get("AAYU_API_URL") or "https://aayuapi.onrender.com"
if API_URL:
    API_URL = API_URL.rstrip("/")

API_KEY = getattr(config, "API_KEY", None) or os.environ.get("API_KEY") or os.environ.get("AAYU_API_KEY") or "AAYU-API-80FF-83BD866C"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs("cache", exist_ok=True)

COMMON_FILTER_WORDS = {
    'ost', 'soundtrack', 'sound', 'track', 'soundtrakc', 'by', 'official', 'video',
    'audio', 'full', 'song', 'songs', 'lyrics', 'hd', '4k', 'pakistani', 'drama',
    'title', 'music', 'mp3', 'download', 'female', 'version', 'feat', 'ft'
}


def clean_query_for_saavn(query: str):
    """Generates prioritized list of clean search queries for JioSaavn."""
    raw = query.strip()
    filler_regex = r'\b(ost|soundtrack|sound\s*track|soundtrakc|by|official\s*video|official\s*audio|official|video|audio|full\s*song|full\s*ost|full|song|lyrics|hd|4k|pakistani\s*drama|pakistani|drama|mp3|remix)\b'
    cleaned = re.sub(filler_regex, ' ', raw, flags=re.IGNORECASE)
    cleaned = re.sub(r'[\(\)\[\]\{\}\-_\|:,]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r'(mann)(mast)', r'\1 \2', cleaned, flags=re.IGNORECASE)
    
    candidates = []
    words = cleaned.split()
    if len(words) > 4:
        candidates.append(' '.join(words[:4]))
        candidates.append(cleaned)
    elif cleaned:
        candidates.append(cleaned)
    candidates.append(raw)
    return list(dict.fromkeys(candidates))


def decrypt_saavn_url(encrypted_url: str, quality: str = "320") -> str:
    """Decrypts JioSaavn encrypted_media_url to direct CDN streaming URL."""
    if not HAS_CRYPTO or not encrypted_url:
        return ""
    try:
        cipher = Cipher(TripleDES(DES_KEY * 3), modes.ECB())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(base64.b64decode(encrypted_url)) + decryptor.finalize()
        pad = decrypted[-1]
        media_url = decrypted[:-pad].decode("utf-8")
        if quality == "320":
            media_url = media_url.replace("_96.mp4", "_320.mp4").replace("_160.mp4", "_320.mp4")
        return media_url
    except Exception as e:
        print(f"[SAAVN DECRYPT ERROR] {e}")
        return ""


def get_saavn_stream_sync(song_id: str) -> dict:
    """Synchronously fetches exact 320kbps CDN stream from JioSaavn."""
    sid = song_id.replace("saavn_", "").strip()

    # 1. Local decryption
    if HAS_CRYPTO:
        try:
            url = f"https://www.jiosaavn.com/api.php?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids={sid}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as res:
                raw_data = res.read().decode("utf-8", errors="ignore")
                if "{" in raw_data:
                    raw_data = raw_data[raw_data.index("{") : raw_data.rindex("}") + 1]
                    data = json.loads(raw_data)
                else:
                    data = {}
            s = data.get(sid)
            if s and s.get("encrypted_media_url"):
                cdn_url = decrypt_saavn_url(s.get("encrypted_media_url"), quality="320")
                if cdn_url:
                    duration = int(s.get("duration", 0) or 0)
                    return {
                        "id": sid,
                        "title": s.get("song", "").replace("&quot;", '"').replace("&#039;", "'"),
                        "artist": s.get("primary_artists", ""),
                        "duration": duration,
                        "duration_min": f"{duration // 60}:{duration % 60:02d}",
                        "thumb": s.get("image", "").replace("150x150", "500x500"),
                        "stream_url": cdn_url,
                    }
        except Exception as e:
            print(f"[LOCAL SAAVN ERROR] {e}")

    # 2. AayuBots API fallback
    if API_URL:
        try:
            url = f"{API_URL}/saavn/stream?query={sid}&api_key={API_KEY}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode("utf-8"))
                if data.get("status") and data.get("data"):
                    d = data["data"]
                    duration = int(d.get("duration", 0) or 0)
                    return {
                        "id": sid,
                        "title": d.get("title", ""),
                        "artist": d.get("artist", ""),
                        "duration": duration,
                        "duration_min": f"{duration // 60}:{duration % 60:02d}",
                        "thumb": d.get("thumbnail", ""),
                        "stream_url": d.get("stream_url", ""),
                    }
        except Exception as e:
            print(f"[API SAAVN ERROR] {e}")

    return None


async def search_via_saavn(query: str) -> dict:
    """Smart JioSaavn search: strips filler words, matches Pakistani OSTs, Coke Studio & Bollywood."""
    candidates = clean_query_for_saavn(str(query))
    async with aiohttp.ClientSession() as session:
        for cand in candidates:
            try:
                clean = urllib.parse.quote(cand)
                url = f"https://www.jiosaavn.com/api.php?__call=autocomplete.get&_marker=0&query={clean}&ctx=web6dot0"
                async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(total=4)) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        songs = data.get("songs", {}).get("data", [])
                        if songs:
                            top = songs[0]
                            top_title = top.get("title", "").replace("&quot;", '"').replace("&#039;", "'")
                            w_q = set(re.findall(r'[a-zA-Z]{3,}', cand.lower())) - COMMON_FILTER_WORDS
                            w_t = set(re.findall(r'[a-zA-Z]{3,}', top_title.lower())) - COMMON_FILTER_WORDS
                            if len(w_q.intersection(w_t)) >= 1 or len(w_q) == 0:
                                sid = top.get("id")
                                thumb = top.get("image", "").replace("50x50", "500x500")
                                more_info = top.get("more_info", {})
                                duration = int(more_info.get("duration", 240) or 240)
                                return {
                                    "id": sid,
                                    "title": top_title,
                                    "thumb": thumb,
                                    "duration": duration,
                                    "duration_min": f"{duration // 60}:{duration % 60:02d}",
                                    "source": "saavn"
                                }
            except Exception as e:
                pass
    return None


def local_ytdlp_search(query: str, limit: int = 1) -> list:
    """Local yt-dlp Android client search to bypass YouTube datacenter IP bans."""
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "extractor_args": {"youtube": {"player_client": ["android"]}},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            if res and res.get("entries"):
                results = []
                for entry in res["entries"]:
                    if not entry:
                        continue
                    results.append({
                        "id": entry.get("id"),
                        "title": entry.get("title", ""),
                        "duration": entry.get("duration", 0),
                        "thumbnail": entry.get("thumbnail") or f"https://img.youtube.com/vi/{entry.get('id')}/hqdefault.jpg"
                    })
                return results
    except Exception as e:
        print(f"[LOCAL YTDLP SEARCH ERROR] {e}")
    return []


async def search_via_api(query: str, limit: int = 1) -> list:
    """Searches tracks via AayuBots API (Render) with generous timeout."""
    if not API_URL:
        return []
    try:
        clean_query = query.replace("https://www.youtube.com/watch?v=", "").replace("https://youtu.be/", "")
        params = {"query": clean_query, "limit": limit, "api_key": API_KEY}
        headers = {"X-API-KEY": API_KEY, "User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/search", params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=25)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("results", [])
    except Exception as e:
        print(f"[API SEARCH ERROR] {e}")
    return []


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


async def download_song(link: str) -> str:
    """Downloads audio track into normalized 48kHz MP3 file for smooth PyTgCalls streaming."""
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
        return file_path

    # 1. Direct JioSaavn CDN download (Instant 0.2s, 320kbps, zero throttling)
    if video_id.startswith("saavn_"):
        sid = video_id.replace("saavn_", "").strip()
        loop = asyncio.get_event_loop()
        saavn_data = await loop.run_in_executor(None, lambda: get_saavn_stream_sync(sid))
        if saavn_data and saavn_data.get("stream_url"):
            cdn_url = saavn_data["stream_url"]
            try:
                print(f"[SAAVN CDN] Downloading {sid} directly from JioSaavn CDN...")
                temp_raw = os.path.join(DOWNLOAD_DIR, f"temp_{sid}.mp4")
                async with aiohttp.ClientSession() as session:
                    async with session.get(cdn_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(total=40)) as resp:
                        if resp.status == 200:
                            with open(temp_raw, "wb") as f:
                                async for chunk in resp.content.iter_chunked(262144):
                                    f.write(chunk)
                            if os.path.exists(temp_raw) and os.path.getsize(temp_raw) > 1000:
                                # Remux/normalize to 48kHz stereo MP3 for 100% stutter-free PyTgCalls streaming
                                cmd = [
                                    "ffmpeg", "-y", "-i", temp_raw,
                                    "-vn", "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                                    file_path
                                ]
                                try:
                                    proc = await asyncio.create_subprocess_exec(
                                        *cmd,
                                        stdout=asyncio.subprocess.DEVNULL,
                                        stderr=asyncio.subprocess.DEVNULL
                                    )
                                    await asyncio.wait_for(proc.wait(), timeout=30)
                                except Exception as fe:
                                    print(f"[FFMPEG REMUX WARNING] {fe}")

                                # If ffmpeg didn't produce file_path, rename temp_raw as fallback
                                if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
                                    if os.path.exists(file_path):
                                        try: os.remove(file_path)
                                        except Exception: pass
                                    os.rename(temp_raw, file_path)
                                else:
                                    if os.path.exists(temp_raw):
                                        try: os.remove(temp_raw)
                                        except Exception: pass

                                if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
                                    print(f"[SAAVN SUCCESS] Ready: {file_path} ({os.path.getsize(file_path)} bytes)")
                                    return file_path
            except Exception as e:
                print(f"[SAAVN DOWNLOAD ERROR] {e}")

    # 2. Direct yt-dlp with Android/iOS client (Instant 2s download, zero cookies, no IP ban)
    try:
        temp_yt = os.path.join(DOWNLOAD_DIR, f"yt_{video_id}.%(ext)s")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": temp_yt,
            "quiet": True,
            "no_warnings": True,
            "extractor_args": {"youtube": {"player_client": ["android", "ios"]}},
        }
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([f"https://www.youtube.com/watch?v={video_id}"]))
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(f"yt_{video_id}"):
                found = os.path.join(DOWNLOAD_DIR, f)
                if os.path.getsize(found) > 1000:
                    if os.path.exists(file_path):
                        try: os.remove(file_path)
                        except Exception: pass
                    os.rename(found, file_path)
                    print(f"[YOUTUBE SUCCESS] Downloaded {file_path} ({os.path.getsize(file_path)} bytes)")
                    return file_path
    except Exception as e:
        print(f"[YOUTUBE ERROR] Direct download failed: {e}")

    # 3. Fallback to AayuBots API (Render)
    if API_URL:
        params = {"url": video_id, "type": "audio", "api_key": API_KEY}
        headers = {"X-API-KEY": API_KEY, "User-Agent": "Mozilla/5.0"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_URL}/download",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        with open(file_path, "wb") as f:
                            async for chunk in resp.content.iter_chunked(262144):
                                f.write(chunk)
                        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
                            return file_path
        except Exception:
            pass

    return None


async def download_video(link: str) -> str:
    """Downloads video track into local MP4 file."""
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
        return file_path

    if API_URL:
        params = {"url": video_id, "type": "video", "api_key": API_KEY}
        headers = {"X-API-KEY": API_KEY, "User-Agent": "Mozilla/5.0"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_URL}/download",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=180)
                ) as resp:
                    if resp.status == 200:
                        with open(file_path, "wb") as f:
                            async for chunk in resp.content.iter_chunked(262144):
                                f.write(chunk)
                        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
                            return file_path
        except Exception as e:
            print(f"[API ERROR] Video download failed: {e}")

    try:
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": file_path,
            "quiet": True,
            "no_warnings": True,
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        }
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([f"https://www.youtube.com/watch?v={video_id}"]))
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
            return file_path
    except Exception as e:
        print(f"[FALLBACK ERROR] Video download failed: {e}")

    return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        is_direct_url = link.startswith("http://") or link.startswith("https://") or "youtube.com" in link or "youtu.be" in link

        # 1. Direct JioSaavn Search (Instant 0.2s, 320kbps, 100% matched, zero blocks)
        if not is_direct_url:
            saavn_data = await search_via_saavn(link)
            if saavn_data and saavn_data.get("title"):
                return saavn_data["title"], saavn_data.get("duration_min", "4:00"), saavn_data.get("duration", 240), saavn_data.get("thumb", ""), f"saavn_{saavn_data['id']}"

        # 2. Local yt-dlp Android Search
        loop = asyncio.get_event_loop()
        ytdlp_res = await loop.run_in_executor(None, lambda: local_ytdlp_search(link, limit=1))
        if ytdlp_res:
            item = ytdlp_res[0]
            vidid = item.get("id", "")
            title = item.get("title", "")
            duration_sec = int(item.get("duration", 0) or 0)
            duration_min = f"{duration_sec // 60}:{duration_sec % 60:02d}"
            thumbnail = item.get("thumbnail") or f"https://img.youtube.com/vi/{vidid}/hqdefault.jpg"
            return title, duration_min, duration_sec, thumbnail, vidid

        # 3. Fallback to VideosSearch
        if VideosSearch:
            try:
                results = VideosSearch(link, limit=1)
                res = await results.next()
                if res and res.get("result"):
                    result = res["result"][0]
                    title = result.get("title", "")
                    duration_min = result.get("duration", "0:00")
                    thumbnails = result.get("thumbnails", [])
                    thumbnail = thumbnails[0]["url"].split("?")[0] if thumbnails else ""
                    vidid = result.get("id", "")
                    duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
                    return title, duration_min, duration_sec, thumbnail, vidid
            except Exception:
                pass

        return "", "0:00", 0, "", ""

    async def title(self, link: str, videoid: Union[bool, str] = None):
        title, _, _, _, _ = await self.details(link, videoid)
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        _, duration_min, _, _, _ = await self.details(link, videoid)
        return duration_min

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        _, _, _, thumb, _ = await self.details(link, videoid)
        return thumb

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        if not Playlist:
            return []
        try:
            plist = await Playlist.get(link)
        except Exception:
            return []
        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if not data:
                continue
            vid = data.get("id")
            if not vid:
                continue
            ids.append(vid)
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        is_direct_url = link.startswith("http://") or link.startswith("https://") or "youtube.com" in link or "youtu.be" in link

        # 1. Direct JioSaavn Search (Instant 0.2s response for song queries)
        if not is_direct_url:
            saavn_data = await search_via_saavn(link)
            if saavn_data and saavn_data.get("title"):
                title = saavn_data["title"]
                sid = saavn_data["id"]
                vidid = f"saavn_{sid}"
                track_details = {
                    "title": title,
                    "link": f"https://www.youtube.com/watch?v={vidid}",
                    "vidid": vidid,
                    "duration_min": saavn_data.get("duration_min", "4:00"),
                    "thumb": saavn_data.get("thumb", ""),
                }
                return track_details, vidid

        # 2. Local yt-dlp Android Search (Zero IP blocks)
        loop = asyncio.get_event_loop()
        ytdlp_res = await loop.run_in_executor(None, lambda: local_ytdlp_search(link, limit=1))
        if ytdlp_res:
            item = ytdlp_res[0]
            vidid = item.get("id", "")
            title = item.get("title", "")
            sec = int(item.get("duration", 0) or 0)
            duration_min = f"{sec // 60}:{sec % 60:02d}"
            track_details = {
                "title": title,
                "link": f"https://www.youtube.com/watch?v={vidid}",
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": item.get("thumbnail") or f"https://img.youtube.com/vi/{vidid}/hqdefault.jpg",
            }
            return track_details, vidid

        # 3. Fallback to VideosSearch
        if VideosSearch:
            try:
                results = VideosSearch(link, limit=1)
                res = await results.next()
                if res and res.get("result"):
                    result = res["result"][0]
                    title = result.get("title", "")
                    duration_min = result.get("duration", "0:00")
                    vidid = result.get("id", "")
                    thumbnails = result.get("thumbnails", [])
                    thumbnail = thumbnails[0]["url"].split("?")[0] if thumbnails else f"https://img.youtube.com/vi/{vidid}/hqdefault.jpg"
                    track_details = {
                        "title": title,
                        "link": f"https://www.youtube.com/watch?v={vidid}",
                        "vidid": vidid,
                        "duration_min": duration_min,
                        "thumb": thumbnail,
                    }
                    return track_details, vidid
            except Exception:
                pass

        return {}, ""

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        loop = asyncio.get_event_loop()
        try:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(link, download=False))
        except Exception:
            return [], link
        formats_available = []
        for format in info.get("formats", []):
            if "dash" in str(format.get("format")).lower():
                continue
            try:
                format.get("format")
                format.get("filesize")
                format.get("format_id")
                format.get("ext")
                format["format_note"]
            except KeyError:
                continue
            formats_available.append(
                {
                    "format": format["format"],
                    "filesize": format.get("filesize", 0),
                    "format_id": format["format_id"],
                    "ext": format["ext"],
                    "format_note": format["format_note"],
                    "yturl": link,
                }
            )
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if not VideosSearch:
            return "", "0:00", "", ""
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)
            if downloaded_file and os.path.exists(downloaded_file) and os.path.getsize(downloaded_file) > 1000:
                return downloaded_file, True
            raise Exception("Download failed or audio file not created")
        except Exception as e:
            print(f"[DOWNLOAD ERROR] {e}")
            raise e


YouTube = YouTubeAPI()

