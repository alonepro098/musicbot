import asyncio
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from Ayush import app
from Ayush.core.call import Aayu
from Ayush.utils.database import is_active_chat
from Ayush.utils.decorators import AdminRightsCheck
from config import BANNED_USERS

ACTIVE_TIMERS = {}


@app.on_message(filters.command(["sleeptimer", "timer", "sleep"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def sleep_timer_handler(client, message: Message, chat_id, _):
    if len(message.command) < 2:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="⏱️ 15 Mins", callback_data=f"SLEEPTIMER_SET|{chat_id}|15"),
                    InlineKeyboardButton(text="⏱️ 30 Mins", callback_data=f"SLEEPTIMER_SET|{chat_id}|30"),
                ],
                [
                    InlineKeyboardButton(text="⏱️ 45 Mins", callback_data=f"SLEEPTIMER_SET|{chat_id}|45"),
                    InlineKeyboardButton(text="⏱️ 60 Mins", callback_data=f"SLEEPTIMER_SET|{chat_id}|60"),
                ],
                [
                    InlineKeyboardButton(text="❌ Cancel Timer", callback_data=f"SLEEPTIMER_CANCEL|{chat_id}"),
                    InlineKeyboardButton(text="🗑️ Close", callback_data="close"),
                ]
            ]
        )
        return await message.reply_text(
            "<blockquote>🌙 <b><u>SMART SLEEP TIMER</u></b>\n\n"
            "💡 <i>Choose a preset or type:</i> <code>/sleeptimer [minutes]</code>\n"
            "The bot will automatically stop streaming and leave when the timer expires!</blockquote>",
            reply_markup=buttons,
        )

    time_arg = message.command[1].lower()
    try:
        if time_arg.endswith("h"):
            minutes = int(time_arg.replace("h", "")) * 60
        elif time_arg.endswith("m"):
            minutes = int(time_arg.replace("m", ""))
        else:
            minutes = int(time_arg)
    except ValueError:
        return await message.reply_text("<blockquote>❌ <b>Invalid time format!</b> Example: <code>/sleeptimer 30m</code> or <code>/sleeptimer 1h</code></blockquote>")

    if minutes <= 0 or minutes > 360:
        return await message.reply_text("<blockquote>❌ <b>Timer must be between 1 minute and 6 hours (360 mins)!</b></blockquote>")

    await start_sleep_timer(chat_id, minutes, message)


async def start_sleep_timer(chat_id: int, minutes: int, message: Message = None):
    # Cancel existing
    if chat_id in ACTIVE_TIMERS:
        ACTIVE_TIMERS[chat_id]["task"].cancel()

    end_time = datetime.now() + timedelta(minutes=minutes)
    
    async def timer_worker():
        try:
            await asyncio.sleep(minutes * 60)
            if await is_active_chat(chat_id):
                try:
                    await Aayu.force_stop_stream(chat_id)
                    await app.send_message(
                        chat_id,
                        "<blockquote>🌙 <b><u>SLEEP TIMER EXPIRED</u></b>\n\n"
                        "😴 <i>Good night! Music has been stopped and bot disconnected. Sweet dreams!</i></blockquote>"
                    )
                except Exception:
                    pass
            if chat_id in ACTIVE_TIMERS:
                del ACTIVE_TIMERS[chat_id]
        except asyncio.CancelledError:
            pass

    task = asyncio.create_task(timer_worker())
    ACTIVE_TIMERS[chat_id] = {
        "end_time": end_time,
        "task": task,
        "minutes": minutes,
    }

    if message:
        await message.reply_text(
            f"<blockquote>🌙 <b><u>SLEEP TIMER ACTIVATED</u></b>\n\n"
            f"⏱️ <b>Duration :</b> {minutes} Minutes\n"
            f"⏰ <b>Auto-Stop Time :</b> <code>{end_time.strftime('%H:%M:%S')}</code>\n\n"
            f"💡 <i>Cancel anytime using <code>/canceltimer</code></i></blockquote>"
        )


@app.on_callback_query(filters.regex(r"^SLEEPTIMER_") & ~BANNED_USERS)
async def sleep_timer_callback(client, CallbackQuery):
    parts = CallbackQuery.data.split("|")
    action = parts[0].split("_")[1]
    chat_id = int(parts[1])

    if action == "CANCEL":
        if chat_id in ACTIVE_TIMERS:
            ACTIVE_TIMERS[chat_id]["task"].cancel()
            del ACTIVE_TIMERS[chat_id]
            await CallbackQuery.edit_message_text("<blockquote>❌ <b>Sleep Timer has been cancelled.</b></blockquote>")
        else:
            await CallbackQuery.answer("No active timer found.", show_alert=True)
    elif action == "SET":
        minutes = int(parts[2])
        await start_sleep_timer(chat_id, minutes)
        await CallbackQuery.edit_message_text(
            f"<blockquote>🌙 <b><u>SLEEP TIMER ACTIVATED</u></b>\n\n"
            f"⏱️ <b>Duration :</b> {minutes} Minutes\n\n"
            f"💡 <i>Cancel anytime using <code>/canceltimer</code></i></blockquote>"
        )


@app.on_message(filters.command(["canceltimer", "stopsleeptimer"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def cancel_timer_handler(client, message: Message, chat_id, _):
    if chat_id in ACTIVE_TIMERS:
        ACTIVE_TIMERS[chat_id]["task"].cancel()
        del ACTIVE_TIMERS[chat_id]
        await message.reply_text("<blockquote>❌ <b>Sleep Timer has been cancelled successfully.</b></blockquote>")
    else:
        await message.reply_text("<blockquote>❌ <b>No active sleep timer in this group!</b></blockquote>")


@app.on_message(filters.command(["timerstatus", "sleeptimerstatus"]) & filters.group & ~BANNED_USERS)
async def timer_status_handler(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in ACTIVE_TIMERS:
        return await message.reply_text("<blockquote>ℹ️ <b>No active sleep timer running.</b></blockquote>")

    timer_info = ACTIVE_TIMERS[chat_id]
    rem = timer_info["end_time"] - datetime.now()
    rem_mins = max(0, int(rem.total_seconds() // 60))
    rem_secs = max(0, int(rem.total_seconds() % 60))

    await message.reply_text(
        f"<blockquote>🌙 <b><u>SLEEP TIMER STATUS</u></b>\n\n"
        f"⏳ <b>Remaining :</b> {rem_mins}m {rem_secs}s\n"
        f"⏰ <b>Auto-Stop Time :</b> <code>{timer_info['end_time'].strftime('%H:%M:%S')}</code></blockquote>"
    )
