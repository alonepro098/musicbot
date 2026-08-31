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


# ================= NEON COLORS =================
NEON_COLORS = [
    ("#ff004f", "#ff2f7d"),  # red
    ("#ff00c8", "#ff4ddb"),  # pink
    ("#00ff99", "#4dffc3"),  # green
    ("#00aaff", "#4dc3ff"),  # blue
    ("#ffd000", "#ffe066"),  # yellow
]


# ================= STYLE 1: NEON CARD =================
def gen_thumb_style1(yt, title, duration, views, videoid):
    # ---------- BACKGROUND ----------
    bg = changeImageSize(1280, 720, yt)
    bg = bg.filter(ImageFilter.GaussianBlur(22))
    bg = ImageEnhance.Brightness(bg).enhance(0.40)

    draw = ImageDraw.Draw(bg)

    # ---------- RANDOM NEON ----------
    glow_color, border_color = random.choice(NEON_COLORS)

    # ---------- CENTER THUMB ----------
    thumb_w, thumb_h = 840, 460
    yt_thumb = yt.resize((thumb_w, thumb_h))

    mask = Image.new("L", (thumb_w, thumb_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, thumb_w, thumb_h), radius=25, fill=255
    )
    yt_thumb.putalpha(mask)

    x = (1280 - thumb_w) // 2
    y = 160

    # ---------- GLOW ----------
    glow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)

    gdraw.rounded_rectangle(
        (x - 25, y - 25, x + thumb_w + 25, y + thumb_h + 25),
        radius=35,
        fill=glow_color,
    )
    glow = glow.filter(ImageFilter.GaussianBlur(35))
    bg.alpha_composite(glow)

    # ---------- BORDER ----------
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

    # ---------- FONTS ----------
    title_font = ImageFont.truetype("Ayush/assets/font.ttf", 46)
    info_font = ImageFont.truetype("Ayush/assets/font2.ttf", 30)
    watermark_font = ImageFont.truetype("Ayush/assets/font2.ttf", 24)

    # ---------- TITLE (TOP RIGHT) ----------
    title_w = draw.textlength(title, font=title_font)
    draw.text(
        (1280 - title_w - 40, 40),
        title,
        font=title_font,
        fill="white",
        stroke_width=2,
        stroke_fill=border_color,
    )

    # ---------- BOTTOM INFO ----------
    username = getattr(app, "username", None) or "MusicBot"
    info_text = f"YouTube : {views} | Time : {duration} | Player : @{username}"
    info_w = draw.textlength(info_text, font=info_font)

    draw.text(
        ((1280 - info_w) // 2, y + thumb_h + 40),
        info_text,
        font=info_font,
        fill=border_color,
    )

    # ---------- WATERMARK ----------
    draw.text(
        (30, 30),
        "AYUSH MUSIC",
        font=watermark_font,
        fill=border_color,
    )

    return bg


# ================= STYLE 2: CIRCLE DISC POSTER =================
def gen_thumb_style2(yt, title, duration, views, videoid):
    # ---------- BACKGROUND ----------
    image1 = changeImageSize(1280, 720, yt)
    image2 = image1.convert("RGBA")
    background = image2.filter(ImageFilter.BoxBlur(28))
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.50)

    # ---------- CIRCLE CROP DISC ----------
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

    # ---------- DISC GLOW & BORDER RING ----------
    glow_color, border_color = random.choice(NEON_COLORS)
    ring = Image.new("RGBA", (395, 395), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(ring)
    rdraw.ellipse((0, 0, 395, 395), fill=glow_color)
    ring = ring.filter(ImageFilter.GaussianBlur(15))
    
    disc_x = int((1280 - 365) / 2)
    disc_y = 120
    
    background.paste(ring, (disc_x - 15, disc_y - 15), mask=ring)
    background.paste(logo, (disc_x, disc_y), mask=logo)

    # Outer neon border around disc
    border_ring = Image.new("RGBA", (375, 375), (0, 0, 0, 0))
    brdraw = ImageDraw.Draw(border_ring)
    brdraw.ellipse((0, 0, 375, 375), outline=border_color, width=5)
    background.paste(border_ring, (disc_x - 5, disc_y - 5), mask=border_ring)

    draw = ImageDraw.Draw(background)
    font_large = ImageFont.truetype("Ayush/assets/font.ttf", 46)
    font_mid = ImageFont.truetype("Ayush/assets/font.ttf", 36)
    font_small = ImageFont.truetype("Ayush/assets/font2.ttf", 28)

    # ---------- HEADER ----------
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

    # ---------- TITLE (WRAPPED 2 LINES) ----------
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

    # ---------- FOOTER DURATION & VIEWS ----------
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


# ================= MAIN =================
async def get_thumb(videoid):
    global THUMB_COUNTER
    out_file = f"cache/{videoid}.png"
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

        # ---------- ALTERNATING THUMBNAIL ENGINE ----------
        # Style 1: Neon Card | Style 2: Circle Disc Poster
        THUMB_COUNTER += 1
        if THUMB_COUNTER % 2 == 1:
            bg = gen_thumb_style1(yt, title, duration, views, videoid)
        else:
            bg = gen_thumb_style2(yt, title, duration, views, videoid)

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
