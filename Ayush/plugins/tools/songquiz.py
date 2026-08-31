import random
import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from Ayush import app
from config import BANNED_USERS

# In-memory quiz sessions and leaderboard
ACTIVE_QUIZZES = {}
QUIZ_SCORES = {}

QUIZ_DB = [
    {
        "snippet": "🎵 <i>'Teri jhuki nazar, teri har ada, mujhe keh rahi hai ye dastaan...'</i>",
        "movie": "Murder 3",
        "artist": "Shafqat Amanat Ali",
        "options": ["Teri Jhuki Nazar", "Tum Hi Ho", "Pee Loon", "Mat Aazma Re"],
        "correct": "Teri Jhuki Nazar",
        "yt_query": "Teri Jhuki Nazar Murder 3",
    },
    {
        "snippet": "🎵 <i>'Kyon ki tum hi ho, ab tum hi ho, zindagi ab tum hi ho...'</i>",
        "movie": "Aashiqui 2",
        "artist": "Arijit Singh",
        "options": ["Sunn Raha Hai", "Tum Hi Ho", "Chahun Main Ya Naa", "Milne Hai Mujhse Aayi"],
        "correct": "Tum Hi Ho",
        "yt_query": "Tum Hi Ho Aashiqui 2",
    },
    {
        "snippet": "🎵 <i>'Kesariya tera ishq hai piya, rang jaaun jo main haath lagaun...'</i>",
        "movie": "Brahmastra",
        "artist": "Arijit Singh",
        "options": ["Rasiya", "Deva Deva", "Kesariya", "Apna Bana Le"],
        "correct": "Kesariya",
        "yt_query": "Kesariya Brahmastra",
    },
    {
        "snippet": "🎵 <i>'Main tenu samjhawan ki, na tere bina lagda jee...'</i>",
        "movie": "Humpty Sharma Ki Dulhania",
        "artist": "Arijit Singh & Shreya Ghoshal",
        "options": ["Samjhawan", "Bolna", "Dillagi", "Naina"],
        "correct": "Samjhawan",
        "yt_query": "Samjhawan Humpty Sharma",
    },
    {
        "snippet": "🎵 <i>'Tere vaaste falak se main chaand laaunga, solah satrah sitaare sang baandh laaunga...'</i>",
        "movie": "Zara Hatke Zara Bachke",
        "artist": "Varun Jain, Sachin-Jigar",
        "options": ["Tere Vaaste", "Phir Aur Kya Chahiye", "Saari Duniya Jalaa Denge", "Heeriye"],
        "correct": "Tere Vaaste",
        "yt_query": "Tere Vaaste Zara Hatke",
    },
    {
        "snippet": "🎵 <i>'Jeene laga hoon pehle se zyada, pehle se zyada tumpe marne laga hoon...'</i>",
        "movie": "Ramaiya Vastavaiya",
        "artist": "Atif Aslam, Shreya Ghoshal",
        "options": ["Rang Jo Lagyo", "Jeene Laga Hoon", "Pehli Nazar Mein", "Tu Jaane Na"],
        "correct": "Jeene Laga Hoon",
        "yt_query": "Jeene Laga Hoon Atif Aslam",
    },
    {
        "snippet": "🎵 <i>'Kaun tujhe yoon pyaar karega jaise main karta hoon...'</i>",
        "movie": "M.S. Dhoni",
        "artist": "Palak Muchhal, Amaal Mallik",
        "options": ["Besabriyaan", "Jab Tak", "Kaun Tujhe", "Phir Kabhi"],
        "correct": "Kaun Tujhe",
        "yt_query": "Kaun Tujhe MS Dhoni",
    },
    {
        "snippet": "🎵 <i>'Tu hai toh mujhe phir aur kya chahiye, kisi ki na madad na panaah chahiye...'</i>",
        "movie": "Zara Hatke Zara Bachke",
        "artist": "Arijit Singh",
        "options": ["Phir Aur Kya Chahiye", "Apna Bana Le", "O Maahi", "Satranga"],
        "correct": "Phir Aur Kya Chahiye",
        "yt_query": "Phir Aur Kya Chahiye",
    },
]


@app.on_message(filters.command(["songquiz", "guessthesong", "musicquiz"]) & filters.group & ~BANNED_USERS)
async def song_quiz_handler(client, message: Message):
    chat_id = message.chat.id
    if chat_id in ACTIVE_QUIZZES:
        return await message.reply_text("⚠️ <i>A quiz is already active in this group! Answer that first or wait for the timer.</i>")

    quiz = random.choice(QUIZ_DB)
    q_id = f"{chat_id}_{random.randint(1000, 9999)}"
    ACTIVE_QUIZZES[chat_id] = {
        "id": q_id,
        "correct": quiz["correct"],
        "yt_query": quiz["yt_query"],
        "answered": False,
    }

    buttons = []
    shuffled_options = list(quiz["options"])
    random.shuffle(shuffled_options)

    # 2x2 inline button grid
    row = []
    for opt in shuffled_options:
        cb = f"QUIZ_ANS|{chat_id}|{opt}"
        row.append(InlineKeyboardButton(text=opt, callback_data=cb))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="🗑️ Cancel Quiz", callback_data=f"QUIZ_CANCEL|{chat_id}")])

    quiz_text = (
        f"<blockquote>🎮 <b><u>GUESS THE SONG CHALLENGE</u></b>\n\n"
        f"{quiz['snippet']}\n\n"
        f"🎬 <b>Movie :</b> {quiz['movie']}\n"
        f"🎤 <b>Singer :</b> {quiz['artist']}\n\n"
        f"⏱️ <i>You have 45 seconds to pick the right song title!</i></blockquote>"
    )

    msg = await message.reply_text(quiz_text, reply_markup=InlineKeyboardMarkup(buttons))

    # Auto expire after 45s
    await asyncio.sleep(45)
    if chat_id in ACTIVE_QUIZZES and ACTIVE_QUIZZES[chat_id]["id"] == q_id and not ACTIVE_QUIZZES[chat_id]["answered"]:
        del ACTIVE_QUIZZES[chat_id]
        try:
            await msg.edit_text(
                f"<blockquote>⏰ <b>Time's Up!</b>\n\n"
                f"The correct song was: <b>{quiz['correct']}</b>\n"
                f"💡 <i>Type /songquiz to try another challenge!</i></blockquote>"
            )
        except Exception:
            pass


@app.on_callback_query(filters.regex(r"^QUIZ_ANS\|") & ~BANNED_USERS)
async def quiz_answer_callback(client, CallbackQuery: CallbackQuery):
    parts = CallbackQuery.data.split("|")
    chat_id = int(parts[1])
    selected_option = parts[2]
    user = CallbackQuery.from_user

    if chat_id not in ACTIVE_QUIZZES:
        return await CallbackQuery.answer("⚠️ This quiz has already expired!", show_alert=True)

    session = ACTIVE_QUIZZES[chat_id]
    if session["answered"]:
        return await CallbackQuery.answer("⚠️ Someone already answered this quiz!", show_alert=True)

    if selected_option == session["correct"]:
        session["answered"] = True
        del ACTIVE_QUIZZES[chat_id]

        # Update leaderboard points
        user_key = f"{chat_id}_{user.id}"
        QUIZ_SCORES[user_key] = QUIZ_SCORES.get(user_key, {"name": user.first_name, "points": 0})
        QUIZ_SCORES[user_key]["points"] += 10
        total_pts = QUIZ_SCORES[user_key]["points"]

        play_btn = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="▶️ Play this song in VC",
                        callback_data=f"CPLAY_SEARCH|{session['yt_query']}"
                    ),
                    InlineKeyboardButton(text="🗑️ Close", callback_data="close"),
                ]
            ]
        )

        await CallbackQuery.edit_message_text(
            f"<blockquote>🎉 <b>CORRECT ANSWER!</b>\n\n"
            f"👑 <b>Winner :</b> {user.mention}\n"
            f"🎵 <b>Song :</b> <code>{session['correct']}</code>\n"
            f"🏆 <b>Points Earned :</b> +10 (Total: {total_pts} pts)\n\n"
            f"<i>Want to listen? Click below to stream it directly!</i></blockquote>",
            reply_markup=play_btn,
        )
    else:
        await CallbackQuery.answer("❌ Wrong answer! Try again or let someone else guess.", show_alert=True)


@app.on_callback_query(filters.regex(r"^QUIZ_CANCEL\|") & ~BANNED_USERS)
async def quiz_cancel_callback(client, CallbackQuery: CallbackQuery):
    parts = CallbackQuery.data.split("|")
    chat_id = int(parts[1])
    if chat_id in ACTIVE_QUIZZES:
        del ACTIVE_QUIZZES[chat_id]
    await CallbackQuery.edit_message_text("<blockquote>🗑️ <b>Song Quiz cancelled.</b></blockquote>")


@app.on_message(filters.command(["quizleaderboard", "quiztop", "musicquiztop"]) & filters.group & ~BANNED_USERS)
async def quiz_leaderboard_handler(client, message: Message):
    chat_id = message.chat.id
    chat_scores = []
    for k, v in QUIZ_SCORES.items():
        if k.startswith(f"{chat_id}_"):
            chat_scores.append(v)

    if not chat_scores:
        return await message.reply_text("<blockquote>📊 <b><u>QUIZ LEADERBOARD</u></b>\n\nNo points scored yet! Start playing with <code>/songquiz</code>!</blockquote>")

    chat_scores.sort(key=lambda x: x["points"], reverse=True)
    text = "<blockquote>🏆 <b><u>MUSIC QUIZ TOP CHAMPIONS</u></b>\n\n"
    medals = ["🥇", "🥈", "🥉", "🎖️", "🎖️"]
    for idx, player in enumerate(chat_scores[:10]):
        m = medals[idx] if idx < len(medals) else f"#{idx+1}"
        text += f"{m} <b>{player['name']}</b> ➜ <code>{player['points']} pts</code>\n"
    text += "</blockquote>"

    await message.reply_text(text)
