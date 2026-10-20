import asyncio
import os
import re
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist
import aiohttp
import config

# ========================================================
# AAYUBOTS CUSTOM MUSIC STREAMING API INTEGRATION
# ========================================================
# Set API_URL and API_KEY in config.py or via environment variables:
# AAYU_API_URL = "http://localhost:8080" (or your deployed domain: https://api.yourdomain.com)
# AAYU_API_KEY = "AAYU-API-XXXX-XXXXXXXX" (get from @testaayu113bot via /getkey)
# ========================================================

API_URL = getattr(config, "API_URL", None) or os.environ.get("API_URL") or os.environ.get("AAYU_API_URL") or os.environ.get("MusicSp_API_URL", "https://tall-peaches-dig.loca.lt")
if API_URL:
    API_URL = API_URL.rstrip("/")

API_KEY = getattr(config, "API_KEY", None) or os.environ.get("API_KEY") or os.environ.get("AAYU_API_KEY") or os.environ.get("MusicSp_API_KEY", "AAYU-API-80FF-83BD866C")

DOWNLOAD_DIR = "downloads"

async def search_via_api(query: str, limit: int = 1) -> list:
    """Searches tracks via AayuBots API (Render) with generous timeout for Render wake-up."""
    if not API_URL:
        return []
    try:
        clean_query = query.replace("https://www.youtube.com/watch?v=", "").replace("https://youtu.be/", "")
        params = {"query": clean_query, "limit": limit, "api_key": API_KEY}
        headers = {"X-API-KEY": API_KEY, "User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/search", params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=35)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("results", [])
    except Exception as e:
        print(f"[API SEARCH ERROR] {e}")
    return []


async def search_via_saavn(query: str) -> dict:
    """Direct JioSaavn search (0.2s instant response, 100% bypasses YouTube IP bans)."""
    try:
        clean = urllib.parse.quote(query)
        url = f"https://www.jiosaavn.com/api.php?__call=autocomplete.get&_marker=0&query={clean}&ctx=web6dot0"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(total=4)) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    songs = data.get("songs", {}).get("data", [])
                    if songs:
                        s = songs[0]
                        title = s.get("title", "").replace("&quot;", '"').replace("&#039;", "'")
                        thumb = s.get("image", "").replace("50x50", "500x500")
                        sid = s.get("id")
                        return {
                            "title": title,
                            "id": sid,
                            "thumb": thumb,
                            "source": "saavn"
                        }
    except Exception as e:
        print(f"[SAAVN SEARCH ERROR] {e}")
    return None


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


async def download_song(link: str) -> str:
    """Downloads audio track via AayuBots API into local MP3 file for PyTgCalls."""
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    # Download from AayuBots API (Render)
    if API_URL:
        params = {"url": video_id, "type": "audio", "api_key": API_KEY}
        headers = {"X-API-KEY": API_KEY, "User-Agent": "Mozilla/5.0"}

        for attempt in range(2):
            try:
                print(f"[API] Downloading audio {video_id} via {API_URL} (Attempt {attempt+1})...")
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{API_URL}/download",
                        params=params,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=120)
                    ) as resp:
                        if resp.status == 200:
                            with open(file_path, "wb") as f:
                                async for chunk in resp.content.iter_chunked(262144):
                                    f.write(chunk)
                            if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
                                print(f"[API SUCCESS] Downloaded {video_id}.mp3 ({os.path.getsize(file_path)} bytes)")
                                return file_path
                        else:
                            print(f"[API ERROR] API returned status {resp.status} for {video_id}")
            except Exception as e:
                print(f"[API ERROR] Download attempt {attempt+1} failed: {e}")
                if os.path.exists(file_path):
                    try: os.remove(file_path)
                    except Exception: pass
            import asyncio
            await asyncio.sleep(1)

    # Fallback to direct yt-dlp if API is temporarily unavailable
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
            "no_warnings": True,
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        }
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([f"https://www.youtube.com/watch?v={video_id}"]))
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
    except Exception as e:
        print(f"[FALLBACK ERROR] Direct download failed: {e}")

    return None


async def download_video(link: str) -> str:
    """Downloads video track via AayuBots API into local MP4 file."""
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    # Download from AayuBots API
    if API_URL:
        params = {"url": video_id, "type": "video", "api_key": API_KEY}
        headers = {"X-API-KEY": API_KEY, "User-Agent": "Mozilla/5.0"}

        try:
            print(f"[API] Downloading video {video_id} via {API_URL}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_URL}/download",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as resp:
                    if resp.status == 200:
                        with open(file_path, "wb") as f:
                            async for chunk in resp.content.iter_chunked(262144):
                                f.write(chunk)
                        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                            return file_path
        except Exception as e:
            print(f"[API ERROR] Video download failed: {e}")
            if os.path.exists(file_path):
                try: os.remove(file_path)
                except Exception: pass

    # Fallback to direct yt-dlp
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
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
    except Exception as e:
        print(f"[FALLBACK ERROR] Direct video download failed: {e}")

    return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        # API search first
        api_results = await search_via_api(link, limit=1)
        if api_results:
            item = api_results[0]
            vidid = item.get("id", "")
            title = item.get("title", "")
            duration_sec = int(item.get("duration", 0) or 0)
            duration_min = f"{duration_sec // 60}:{duration_sec % 60:02d}"
            thumbnail = item.get("thumbnail", "")
            return title, duration_min, duration_sec, thumbnail, vidid

        # Fallback to local VideosSearch
        try:
            results = VideosSearch(link, limit=1)
            res = await results.next()
            if not res or not res.get("result"):
                return "", "0:00", 0, "", ""
            for result in res["result"]:
                title = result.get("title", "")
                duration_min = result.get("duration", "0:00")
                thumbnails = result.get("thumbnails", [])
                thumbnail = thumbnails[0]["url"].split("?")[0] if thumbnails else ""
                vidid = result.get("id", "")
                duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
            return title, duration_min, duration_sec, thumbnail, vidid
        except Exception:
            return "", "0:00", 0, "", ""

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        res = await results.next()
        if res and res.get("result"):
            for result in res["result"]:
                return result.get("title", "")
        return ""

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        res = await results.next()
        if res and res.get("result"):
            for result in res["result"]:
                return result.get("duration", "0:00")
        return "0:00"

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        res = await results.next()
        if res and res.get("result"):
            for result in res["result"]:
                thumbnails = result.get("thumbnails", [])
                return thumbnails[0]["url"].split("?")[0] if thumbnails else ""
        return ""

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

        # 1. If text query, try JioSaavn 0.2s search first for instant response
        if not is_direct_url:
            saavn_data = await search_via_saavn(link)
            if saavn_data and saavn_data.get("title"):
                title = saavn_data["title"]
                sid = saavn_data["id"]
                track_details = {
                    "title": title,
                    "link": f"https://www.youtube.com/watch?v={sid}",
                    "vidid": sid,
                    "duration_min": "3:45",
                    "thumb": saavn_data.get("thumb", ""),
                }
                return track_details, sid

        # 2. Try AayuBots API search (Render yt-dlp Android client)
        api_results = await search_via_api(link, limit=1)
        if api_results:
            item = api_results[0]
            vidid = item.get("id", "")
            title = item.get("title", "")
            sec = int(item.get("duration", 0) or 0)
            duration_min = f"{sec // 60}:{sec % 60:02d}"
            track_details = {
                "title": title,
                "link": f"https://www.youtube.com/watch?v={vidid}",
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": item.get("thumbnail", ""),
            }
            return track_details, vidid

        # 3. Fallback to local VideosSearch
        try:
            results = VideosSearch(link, limit=1)
            res = await results.next()
            if res and res.get("result"):
                result = res["result"][0]
                title = result.get("title", "")
                duration_min = result.get("duration", "0:00")
                vidid = result.get("id", "")
                yturl = result.get("link", "")
                thumbnails = result.get("thumbnails", [])
                thumbnail = thumbnails[0]["url"].split("?")[0] if thumbnails else ""
                track_details = {
                    "title": title,
                    "link": yturl,
                    "vidid": vidid,
                    "duration_min": duration_min,
                    "thumb": thumbnail,
                }
                return track_details, vidid
        except Exception:
            pass

        raise Exception("No results found")

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except Exception:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        res = await a.next()
        result = res.get("result") if res else []
        if not result or query_type >= len(result):
            return "", "0:00", "", ""
        title = result[query_type].get("title", "")
        duration_min = result[query_type].get("duration", "0:00")
        vidid = result[query_type].get("id", "")
        thumbnails = result[query_type].get("thumbnails", [])
        thumbnail = thumbnails[0]["url"].split("?")[0] if thumbnails else ""
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
            if downloaded_file and os.path.exists(downloaded_file):
                return downloaded_file, True
            raise Exception("Download failed or audio file not created")
        except Exception as e:
            print(f"[DOWNLOAD ERROR] {e}")
            raise e


YouTube = YouTubeAPI()
