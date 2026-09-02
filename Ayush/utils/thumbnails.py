import os
import re
import random
import textwrap
import aiofiles
import aiohttp

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from Ayush import app

# Counter for alternating styles
THUMB_COUNTER = 0

# ================= UTILS =================
def changeImageSize(maxWidth, maxHeight, image):
    ratio = max(maxWidth / image.size[0], maxHeight / image.size[1])
    return image.resize(
        (int(image.size[0] * ratio), int(image.size[1] * ratio)),
        Image.LANCZOS
    )


def clean_title(text):
    text = re.sub(r"\W+", " ", text)
    return text.strip()[:50]


def add_corners(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.LANCZOS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)


async def _get_user_dp(user_id):
    if not user_id:
        return None
    try:
        user = await app.get_users(user_id)
        if user and user.photo:
            file_id = user.photo.big_file_id
            local_path = await app.download_media(file_id, file_name=f"cache/user_{user_id}.jpg")
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
    bg = changeImageSize(1280, 720, yt)
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

    title_font = ImageFont.truetype("Ayush/assets/font.ttf", 46)
    info_font = ImageFont.truetype("Ayush/assets/font2.ttf", 30)
    watermark_font = ImageFont.truetype("Ayush/assets/font2.ttf", 24)

    title_w = draw.textlength(title, font=title_font)
    draw.text(
        (1280 - title_w - 40, 40),
        title,
        font=title_font,
        fill="white",
        stroke_width=2,
        stroke_fill=border_color,
    )

    username = getattr(app, "username", None) or "MusicBot"
    info_text = f"YouTube : {views} | Time : {duration} | Player : @{username}"
    info_w = draw.textlength(info_text, font=info_font)

    draw.text(
        ((1280 - info_w) // 2, y + thumb_h + 40),
        info_text,
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
    image1 = changeImageSize(1280, 720, yt)
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
    font_large = ImageFont.truetype("Ayush/assets/font.ttf", 46)
    font_mid = ImageFont.truetype("Ayush/assets/font.ttf", 36)
    font_small = ImageFont.truetype("Ayush/assets/font2.ttf", 28)

    header_text = "✦ STARTED PLAYING ✦"
    hw = draw.textlength(header_text, font=font_large)
    draw.text(
        ((1280 - hw) / 2, 35),
        header_text,
        fill="white",
        stroke_width=2,
        stroke_fill=border_color,
        font=font_large,
    )

    para = textwrap.wrap(title, width=35)
    try:
        if len(para) > 0 and para[0]:
            tw1 = draw.textlength(para[0], font=font_mid)
            draw.text(
                ((1280 - tw1) / 2, 515),
                para[0],
                fill="white",
                stroke_width=1,
                stroke_fill="white",
                font=font_mid,
            )
        if len(para) > 1 and para[1]:
            tw2 = draw.textlength(para[1], font=font_mid)
            draw.text(
                ((1280 - tw2) / 2, 565),
                para[1],
                fill="white",
                stroke_width=1,
                stroke_fill="white",
                font=font_mid,
            )
    except Exception:
        pass

    username = getattr(app, "username", None) or "MusicBot"
    duration_text = f"⏱️ {duration} Mins | 👁️ {views} Views | @{username}"
    dw = draw.textlength(duration_text, font=font_small)
    draw.text(
        ((1280 - dw) / 2, 645),
        duration_text,
        fill=border_color,
        font=font_small,
    )
    return background


# ================= STYLE 3: FALLENMUSIC CIRCLE DISK + USER DP =================
def gen_thumb_style3(yt, title, duration, views, videoid, user_img=None):
    image1 = changeImageSize(1280, 720, yt)
    image2 = image1.convert("RGBA")
    background = image2.filter(ImageFilter.BoxBlur(30))
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.60)

    # Use circle.png asset
    circle_asset = "Ayush/assets/circle.png"
    if os.path.exists(circle_asset):
        try:
            bg_circle = Image.open(circle_asset).convert("RGBA")
            image3 = changeImageSize(1280, 720, bg_circle)
        except Exception:
            image3 = None
    else:
        image3 = None

    # Big circular crop for YouTube song thumbnail
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

    # Small circular crop for User DP at position (710, 427) size 107x107
    if user_img:
        try:
            u_img = changeImageSize(107, 107, user_img).convert("RGBA")
            u_img = u_img.resize((107, 107), Image.LANCZOS)
            add_corners(u_img)
            
            # White border circle around user DP
            border_dp = Image.new("RGBA", (107, 107), (0, 0, 0, 0))
            b_draw = ImageDraw.Draw(border_dp)
            b_draw.ellipse((0, 0, 107, 107), outline="white", width=3)
            u_img.alpha_composite(border_dp)
            
            background.paste(u_img, (710, 427), mask=u_img)
        except Exception:
            pass
    else:
        # Default circular avatar badge
        default_dp = Image.new("RGBA", (107, 107), (0, 0, 0, 0))
        d_draw = ImageDraw.Draw(default_dp)
        d_draw.ellipse((0, 0, 107, 107), fill=(75, 75, 105, 255), outline="white", width=3)
        background.paste(default_dp, (710, 427), mask=default_dp)

    # Overlay circle.png frame
    if image3:
        background.paste(image3, (0, 0), mask=image3)

    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("Ayush/assets/font.ttf", 45)
    arial = ImageFont.truetype("Ayush/assets/font2.ttf", 30)

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

    username = getattr(app, "username", None) or "MusicBot"
    dur_text = f"Duration: {duration} Mins | Views: {views} | @{username}"
    dw = draw.textlength(dur_text, font=arial)
    draw.text(
        ((1280 - dw) / 2, 660),
        dur_text,
        fill="white",
        font=arial,
    )
    return background


# ================= MAIN =================
async def get_thumb(videoid, user_id=None):
    global THUMB_COUNTER
    out_file = f"cache/{videoid}_{user_id}.png" if user_id else f"cache/{videoid}.png"
    if os.path.isfile(out_file):
        return out_file

    try:
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        data = (await results.next())["result"][0]

        title = clean_title(data["title"])
        duration = data.get("duration", "0:00")
        views = data.get("viewCount", {}).get("short", "Unknown")
        thumb_url = data["thumbnails"][0]["url"].split("?")[0]

        # ---------- DOWNLOAD THUMB ----------
        temp_file = f"cache/temp_{videoid}.png"
        async with aiohttp.ClientSession() as s:
            async with s.get(thumb_url) as r:
                async with aiofiles.open(temp_file, "wb") as f:
                    await f.write(await r.read())

        yt = Image.open(temp_file).convert("RGBA")

        # ---------- DOWNLOAD USER DP ----------
        user_img = await _get_user_dp(user_id)

        # ---------- 3-WAY ALTERNATING THUMBNAIL ENGINE ----------
        # Style 1: Neon Card | Style 2: Circle Disc Poster | Style 3: FallenMusic Circle Disc Frame + User DP
        THUMB_COUNTER += 1
        rem = THUMB_COUNTER % 3
        if rem == 1:
            bg = gen_thumb_style1(yt, title, duration, views, videoid, user_img)
        elif rem == 2:
            bg = gen_thumb_style2(yt, title, duration, views, videoid, user_img)
        else:
            bg = gen_thumb_style3(yt, title, duration, views, videoid, user_img)

        # ---------- SAVE ----------
        os.makedirs("cache", exist_ok=True)
        bg.save(out_file)
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
        return out_file

    except Exception as e:
        print("Thumbnail error:", e)
        return YOUTUBE_IMG_URL
