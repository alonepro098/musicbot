import random
import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Ayush import app
from config import BANNED_USERS

QUOTES = [
    "“The only way to do great work is to love what you do.” – Steve Jobs",
    "“Life is what happens when you’re busy making other plans.” – John Lennon",
    "“Music expresses that which cannot be put into words and that which cannot remain silent.” – Victor Hugo",
    "“Without music, life would be a mistake.” – Friedrich Nietzsche",
    "“One good thing about music, when it hits you, you feel no pain.” – Bob Marley",
    "“Success is not final, failure is not fatal: it is the courage to continue that counts.” – Winston Churchill",
    "“Believe you can and you're halfway there.” – Theodore Roosevelt",
    "“Turn your wounds into wisdom.” – Oprah Winfrey",
]

SHAYARIS = [
    "दिल की महफ़िल में उजाला हो गया,\nजब से तुम आये ज़माना हो गया। ✨",
    "हवाओं का रुख मोड़ देंगे हम,\nतुम्हारी ख़ुशी के लिए खुद को भी छोड़ देंगे हम। 🥀",
    "सुरों की दुनिया में हम ऐसे खो गए,\nतेरे हर एक गीत के दीवाने हो गए। 🎶",
    "रास्ते मुश्किल हैं पर हम मंज़िल पाएंगे,\nये जो किस्मत अकड़ रही है इसे भी हराएंगे। 🔥",
    "चुपके से आकर इस दिल में समा गए,\nसांसों में घुल के मेरी जान बन गए। 💖",
]

JOKES = [
    "Teacher: Why are you late?\nStudent: There was a sign on the road that said 'Go Slow, School Ahead' so I walked slow! 😂",
    "Doctor: Aapko aaraam ki zarurat hai, ye lo sleeping pills.\nPatient: Ye meri biwi ko kab du?\nDoctor: Ye unhe nahi, aapko khaani hai! 🤣",
    "Why do we press harder on a remote control when we know the batteries are weak? Because hope never dies! 📺",
    "What do you call a fake noodle? An Impasta! 🍝",
]

TRUTHS = [
    "What is the most embarrassing thing in your search history? 🤫",
    "What is one secret you have never told anyone in this group? 🤐",
    "Who is your secret crush right now? 💕",
    "What is the biggest lie you ever told your parents? 🙈",
    "What is the weirdest habit you have when you're alone? 🤪",
]

DARES = [
    "Send your most recent selfie in this chat right now! 📸",
    "Change your Telegram bio to 'I am in love with this Music Bot 🎵' for 1 hour! ⚡",
    "Voice message yourself singing your favorite song for 15 seconds! 🎤",
    "Tag the 3rd person in your chat list and say 'You owe me a treat!' 🍔",
    "Send a funny voice message introducing yourself like an anime villain! 😈",
]


@app.on_message(filters.command(["quote"]) & ~BANNED_USERS)
async def quote_handler(client, message: Message):
    quote = random.choice(QUOTES)
    await message.reply_text(
        f"<blockquote>📜 <b><u>ǫᴜᴏᴛᴇ ᴏғ ᴛʜᴇ ᴍᴏᴍᴇɴᴛ :</u></b>\n\n<i>{quote}</i></blockquote>"
    )


@app.on_message(filters.command(["shayari"]) & ~BANNED_USERS)
async def shayari_handler(client, message: Message):
    shayari = random.choice(SHAYARIS)
    await message.reply_text(
        f"<blockquote>🥀 <b><u>sʜᴀʏᴀʀɪ :</u></b>\n\n<b>{shayari}</b></blockquote>"
    )


@app.on_message(filters.command(["joke"]) & ~BANNED_USERS)
async def joke_handler(client, message: Message):
    joke = random.choice(JOKES)
    await message.reply_text(
        f"<blockquote>🤣 <b><u>ᴊᴏᴋᴇ :</u></b>\n\n{joke}</blockquote>"
    )


@app.on_message(filters.command(["truth"]) & ~BANNED_USERS)
async def truth_handler(client, message: Message):
    truth = random.choice(TRUTHS)
    await message.reply_text(
        f"<blockquote>🎲 <b><u>ᴛʀᴜᴛʜ :</u></b>\n\n<b>{truth}</b></blockquote>"
    )


@app.on_message(filters.command(["dare"]) & ~BANNED_USERS)
async def dare_handler(client, message: Message):
    dare = random.choice(DARES)
    await message.reply_text(
        f"<blockquote>🔥 <b><u>ᴅᴀʀᴇ :</u></b>\n\n<b>{dare}</b></blockquote>"
    )


@app.on_message(filters.command(["qr"]) & ~BANNED_USERS)
async def qr_code_handler(client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text(
            "<blockquote><b>💡 <u>ᴜsᴀɢᴇ :</u></b>\n\n<code>/qr [ᴛᴇxᴛ ᴏʀ ᴜʀʟ]</code></blockquote>"
        )

    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    else:
        text = message.text.split(None, 1)[1]

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={text}"
    await message.reply_photo(
        photo=qr_url,
        caption=f"<blockquote>📱 <b><u>ǫʀ ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ</u></b>\n\n<b>ᴄᴏɴᴛᴇɴᴛ :</b> <code>{text[:60]}</code></blockquote>",
    )
