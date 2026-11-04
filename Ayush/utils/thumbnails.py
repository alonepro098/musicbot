import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
import random
import textwrap
import config

try:
    from config import YOUTUBE_IMG_URL
except Exception:
    YOUTUBE_IMG_URL = "https://i.ibb.co/NnfW2VRQ/file-3734.jpg"

try:
    from Ayush import app
except Exception:
    app = None

THUMB_COUNTER = 0


# ================= HELPERS =================
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newRatio = widthRatio if widthRatio < heightRatio else heightRatio
    newWidth = int(round(image.size[0] * newRatio))
    newHeight = int(round(image.size[1] * newRatio))
    newImage = image.resize((newWidth, newHeight))
    return newImage


def add_corners(im, rad=100):
    circle = Image.new("L", (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new("L", im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def clean_title(title: str, max_chars: int = 38) -> str:
    title = re.sub(r"\(.*?\)|\[.*?\]", "", title)
    title = re.sub(r"[\"\'|#@*:]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title[:max_chars].strip()


async def _get_user_dp(user_id):
    if not user_id or not app:
        return None
    try:
        photos = [p async for p in app.get_chat_photos(user_id, limit=1)]
        if photos:
            local_path = await app.download_media(photos[0].file_id, file_name=f"cache/user_{user_id}.jpg")
            if local_path and os.path.exists(local_path):
                img = Image.open(local_path).convert("RGBA")
                return img
    except Exception:
        pass

    # Fallback to bot profile avatar
    try:
        me = await app.get_me()
        if me and me.photo:
            file_id = me.photo.big_file_id
            local_path = await app.download_media(file_id, file_name="cache/bot_pfp.jpg")
            if local_path and os.path.exists(local_path):
                img = Image.open(local_path).convert("RGBA")
                return img
    except Exception:
        pass
    return None


# ================= NEON COLORS =================
NEON_COLORS = [
    ("#ff004f", "#ff2f7d"),  # red
    ("#ff00c8", "#ff4ddb"),  # pink
    ("#00ff99", "#4dffc3"),  # green
    ("#00aaff", "#4dc3ff"),  # blue
    ("#ffd000", "#ffe066"),  # yellow
]


# ================= STYLE 1: NEON CARD =================
def gen_thumb_style1(yt, title, duration, views, videoid, user_img=None):
    bg = yt.resize((1280, 720))
    bg = bg.filter(ImageFilter.GaussianBlur(22))
    bg = ImageEnhance.Brightness(bg).enhance(0.40)

    draw = ImageDraw.Draw(bg)
    glow_color, border_color = random.choice(NEON_COLORS)

    thumb_w, thumb_h = 840, 460
    yt_thumb = yt.resize((thumb_w, thumb_h))

    mask = Image.new("L", (thumb_w, thumb_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, thumb_w, thumb_h), radius=25, fill=255
    )
    yt_thumb.putalpha(mask)

    x = (1280 - thumb_w) // 2
    y = 160

    glow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.rounded_rectangle(
        (x - 25, y - 25, x + thumb_w + 25, y + thumb_h + 25),
        radius=35,
        fill=glow_color,
    )
    glow = glow.filter(ImageFilter.GaussianBlur(35))
    bg.alpha_composite(glow)

    border = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(border)
    bdraw.rounded_rectangle(
        (x - 6, y - 6, x + thumb_w + 6, y + thumb_h + 6),
        radius=30,
        outline=border_color,
        width=6,
    )
    bg.alpha_composite(border)
    bg.paste(yt_thumb, (x, y), yt_thumb)

    try:
        title_font = ImageFont.truetype("Ayush/assets/font.ttf", 46)
        info_font = ImageFont.truetype("Ayush/assets/font2.ttf", 30)
        watermark_font = ImageFont.truetype("Ayush/assets/font2.ttf", 24)
    except Exception:
        title_font = ImageFont.load_default()
        info_font = ImageFont.load_default()
        watermark_font = ImageFont.load_default()

    title_w = draw.textlength(title, font=title_font)
    draw.text(
        (1280 - title_w - 40, 40),
        title,
        font=title_font,
        fill="white",
    )

    draw.text(
        (40, 650),
        f"TIME: {duration}",
        font=info_font,
        fill=border_color,
    )

    vw = draw.textlength(f"VIEWS: {views}", font=info_font)
    draw.text(
        (1280 - vw - 40, 650),
        f"VIEWS: {views}",
        font=info_font,
        fill=border_color,
    )

    draw.text(
        (30, 30),
        "AYUSH MUSIC",
        font=watermark_font,
        fill=border_color,
    )
    return bg


# ================= STYLE 2: CIRCLE DISC POSTER =================
def gen_thumb_style2(yt, title, duration, views, videoid, user_img=None):
    image1 = yt.resize((1280, 720))
    image2 = image1.convert("RGBA")
    background = image2.filter(ImageFilter.BoxBlur(28))
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.50)

    Xcenter = yt.width / 2
    Ycenter = yt.height / 2
    crop_size = min(yt.width, yt.height) // 2
    x1 = max(0, Xcenter - crop_size)
    y1 = max(0, Ycenter - crop_size)
    x2 = min(yt.width, Xcenter + crop_size)
    y2 = min(yt.height, Ycenter + crop_size)
    
    logo = yt.crop((x1, y1, x2, y2)).convert("RGBA")
    logo = logo.resize((365, 365), Image.LANCZOS)
    add_corners(logo)

    glow_color, border_color = random.choice(NEON_COLORS)
    ring = Image.new("RGBA", (395, 395), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(ring)
    rdraw.ellipse((0, 0, 395, 395), fill=glow_color)
    ring = ring.filter(ImageFilter.GaussianBlur(15))
    
    disc_x = int((1280 - 365) / 2)
    disc_y = 120
    
    background.paste(ring, (disc_x - 15, disc_y - 15), mask=ring)
    background.paste(logo, (disc_x, disc_y), mask=logo)

    border_ring = Image.new("RGBA", (375, 375), (0, 0, 0, 0))
    brdraw = ImageDraw.Draw(border_ring)
    brdraw.ellipse((0, 0, 375, 375), outline=border_color, width=5)
    background.paste(border_ring, (disc_x - 5, disc_y - 5), mask=border_ring)

    draw = ImageDraw.Draw(background)
    try:
        font_large = ImageFont.truetype("Ayush/assets/font.ttf", 46)
        font_mid = ImageFont.truetype("Ayush/assets/font.ttf", 36)
        font_small = ImageFont.truetype("Ayush/assets/font2.ttf", 28)
    except Exception:
        font_large = ImageFont.load_default()
        font_mid = ImageFont.load_default()
        font_small = ImageFont.load_default()

    header_text = "NOW PLAYING"
    hw = draw.textlength(header_text, font=font_large)
    draw.text(
        ((1280 - hw) / 2, 35),
        header_text,
        fill="white",
        stroke_width=2,
        stroke_fill=border_color,
        font=font_large,
    )

    tw = draw.textlength(title, font=font_mid)
    draw.text(
        ((1280 - tw) / 2, 520),
        title,
        fill="white",
        font=font_mid,
    )

    info_str = f"Duration: {duration} min   |   Views: {views}"
    iw = draw.textlength(info_str, font=font_small)
    draw.text(
        ((1280 - iw) / 2, 590),
        info_str,
        fill=glow_color,
        font=font_small,
    )

    # User Profile Avatar badge at bottom right
    if user_img:
        try:
            u_img = user_img.resize((90, 90), Image.LANCZOS)
            add_corners(u_img, rad=45)
            background.paste(u_img, (1140, 590), mask=u_img)
        except Exception:
            pass

    return background


# ================= STYLE 3: FALLENMUSIC DISC FRAME + USER DP =================
def gen_thumb_style3(yt, title, duration, views, videoid, user_img=None):
    image1 = yt.resize((1280, 720))
    image2 = image1.convert("RGBA")
    background = image2.filter(ImageFilter.BoxBlur(20))
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.55)

    circle_asset = "Ayush/assets/circle.png"
    if os.path.exists(circle_asset):
        try:
            bg_circle = Image.open(circle_asset).convert("RGBA")
            image3 = changeImageSize(1280, 720, bg_circle)
        except Exception:
            image3 = None
    else:
        image3 = None

    # Big circular crop for song thumbnail
    Xcenter = yt.width / 2
    Ycenter = yt.height / 2
    crop_size = min(yt.width, yt.height) // 2
    x1 = max(0, Xcenter - crop_size)
    y1 = max(0, Ycenter - crop_size)
    x2 = min(yt.width, Xcenter + crop_size)
    y2 = min(yt.height, Ycenter + crop_size)
    
    logo = yt.crop((x1, y1, x2, y2)).convert("RGBA")
    logo = logo.resize((365, 365), Image.LANCZOS)
    add_corners(logo)

    width = int((1280 - 365) / 2)
    background.paste(logo, (width + 2, 138), mask=logo)

    # Small circular crop for User DP
    if user_img:
        try:
            u_img = user_img.resize((107, 107), Image.LANCZOS)
            add_corners(u_img)
            border_dp = Image.new("RGBA", (107, 107), (0, 0, 0, 0))
            b_draw = ImageDraw.Draw(border_dp)
            b_draw.ellipse((0, 0, 107, 107), outline="white", width=3)
            u_img.alpha_composite(border_dp)
            background.paste(u_img, (710, 427), mask=u_img)
        except Exception:
            pass
    else:
        default_dp = Image.new("RGBA", (107, 107), (0, 0, 0, 0))
        d_draw = ImageDraw.Draw(default_dp)
        d_draw.ellipse((0, 0, 107, 107), fill=(75, 75, 105, 255), outline="white", width=3)
        background.paste(default_dp, (710, 427), mask=default_dp)

    if image3:
        background.paste(image3, (0, 0), mask=image3)

    draw = ImageDraw.Draw(background)
    try:
        font = ImageFont.truetype("Ayush/assets/font.ttf", 45)
        arial = ImageFont.truetype("Ayush/assets/font2.ttf", 30)
    except Exception:
        font = ImageFont.load_default()
        arial = ImageFont.load_default()

    header_text = "STARTED PLAYING"
    hw = draw.textlength(header_text, font=font)
    draw.text(
        ((1280 - hw) / 2, 25),
        header_text,
        fill="white",
        stroke_width=2,
        stroke_fill="grey",
        font=font,
    )

    para = textwrap.wrap(title, width=32)
    try:
        if len(para) > 0 and para[0]:
            tw1 = draw.textlength(para[0], font=font)
            draw.text(
                ((1280 - tw1) / 2, 530),
                para[0],
                fill="white",
                stroke_width=1,
                stroke_fill="white",
                font=font,
            )
        if len(para) > 1 and para[1]:
            tw2 = draw.textlength(para[1], font=font)
            draw.text(
                ((1280 - tw2) / 2, 580),
                para[1],
                fill="white",
                stroke_width=1,
                stroke_fill="white",
                font=font,
            )
    except Exception:
        pass

    dur_text = f"Duration: {duration} Mins"
    dw = draw.textlength(dur_text, font=arial)
    draw.text(
        ((1280 - dw) / 2, 660),
        dur_text,
        fill="white",
        font=arial,
    )
    return background


# ================= MAIN =================
async def get_thumb(videoid, user_id=None, custom_thumb=None, title=None, duration=None):
    global THUMB_COUNTER
    os.makedirs('cache', exist_ok=True)
    out_file = f"cache/{videoid}_{user_id}.png" if user_id else f"cache/{videoid}.png"
    if os.path.isfile(out_file) and os.path.getsize(out_file) > 1000:
        return out_file

    temp_file = f"cache/temp_{videoid}.jpg"

    thumb_urls = []
    if custom_thumb and str(custom_thumb).startswith("http"):
        thumb_urls.append(custom_thumb)

    if str(videoid).startswith("saavn_"):
        sid = str(videoid).replace("saavn_", "").strip()
        try:
            from Ayush.platforms.Youtube import get_saavn_stream_sync
            sdata = get_saavn_stream_sync(sid)
            if sdata and sdata.get("thumb"):
                thumb_urls.append(sdata["thumb"])
        except Exception:
            pass
    else:
        thumb_urls.extend([
            f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg",
            f"https://img.youtube.com/vi/{videoid}/hqdefault.jpg",
            f"https://i.ytimg.com/vi/{videoid}/hqdefault.jpg",
        ])

    downloaded = False
    async with aiohttp.ClientSession() as s:
        for t_url in thumb_urls:
            try:
                async with s.get(t_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(total=8)) as r:
                    if r.status == 200:
                        data = await r.read()
                        if len(data) > 1500:
                            async with aiofiles.open(temp_file, "wb") as f:
                                await f.write(data)
                            downloaded = True
                            break
            except Exception:
                continue

    if not downloaded:
        return YOUTUBE_IMG_URL

    try:
        yt = Image.open(temp_file).convert("RGBA")
    except Exception as e:
        print("Failed to open temp thumbnail:", e)
        return temp_file

    # Metadata
    clean_meta_title = clean_title(title) if title else ""
    meta_dur = duration if duration else ""
    views = "320kbps HD"

    if str(videoid).startswith("saavn_"):
        sid = str(videoid).replace("saavn_", "").strip()
        views = "320kbps HD"
        if not clean_meta_title or not meta_dur:
            try:
                from Ayush.platforms.Youtube import get_saavn_stream_sync
                sdata = get_saavn_stream_sync(sid)
                if sdata:
                    clean_meta_title = clean_meta_title or clean_title(sdata.get("title", ""))
                    meta_dur = meta_dur or sdata.get("duration_min", "")
            except Exception:
                pass
    else:
        try:
            url = f"https://www.youtube.com/watch?v={videoid}"
            results = VideosSearch(url, limit=1)
            res = await results.next()
            if res and res.get("result"):
                data = res["result"][0]
                clean_meta_title = clean_meta_title or clean_title(data.get("title", ""))
                meta_dur = meta_dur or data.get("duration", "03:45")
                views = data.get("viewCount", {}).get("short", "1.2M")
        except Exception:
            pass

    title = clean_meta_title or "Playing Music"
    duration = meta_dur or "03:45"

    user_img = await _get_user_dp(user_id)

    try:
        THUMB_COUNTER += 1
        rem = THUMB_COUNTER % 3
        if rem == 1:
            bg = gen_thumb_style1(yt, title, duration, views, videoid, user_img)
        elif rem == 2:
            bg = gen_thumb_style2(yt, title, duration, views, videoid, user_img)
        else:
            bg = gen_thumb_style3(yt, title, duration, views, videoid, user_img)

        bg.save(out_file)
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
        return out_file
    except Exception as e:
        print("Thumbnail generation style error:", e)
        return temp_file
