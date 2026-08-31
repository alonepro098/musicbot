import os
import shutil
from pyrogram import filters
from pyrogram.types import Message

from Ayush import app
from Ayush.misc import SUDOERS
from config import BANNED_USERS


@app.on_message(filters.command(["clean", "clearcache", "clear"]) & SUDOERS & ~BANNED_USERS)
async def clean_cache_handler(client, message: Message):
    m = await message.reply_text("<blockquote>🧹 <b>ᴄʟᴇᴀɴɪɴɢ ᴛᴇᴍᴘᴏʀᴀʀʏ ᴄᴀᴄʜᴇ ғɪʟᴇs...</b></blockquote>")

    deleted_count = 0
    deleted_size = 0

    dirs_to_clean = ["cache", "downloads", "raw_files"]
    for d in dirs_to_clean:
        if os.path.exists(d):
            for filename in os.listdir(d):
                filepath = os.path.join(d, filename)
                try:
                    if os.path.isfile(filepath) or os.path.islink(filepath):
                        deleted_size += os.path.getsize(filepath)
                        os.unlink(filepath)
                        deleted_count += 1
                except Exception:
                    pass

    size_mb = deleted_size / (1024 * 1024)
    await m.edit_text(
        f"<blockquote>✅ <b><u>ᴄᴀᴄʜᴇ ᴄʟᴇᴀɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ !</u></b>\n\n"
        f"🗑️ <b>ғɪʟᴇs ᴅᴇʟᴇᴛᴇᴅ :</b> <code>{deleted_count}</code>\n"
        f"💾 <b>sᴘᴀᴄᴇ ғʀᴇᴇᴅ :</b> <code>{size_mb:.2f} ᴍʙ</code></blockquote>"
    )
