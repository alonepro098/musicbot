import os
import asyncio
from pyrogram import filters
from pyrogram.types import Message

from Ayush import app
from config import BANNED_USERS


@app.on_message(filters.command(["extract", "toaudio"]) & ~BANNED_USERS)
async def extract_audio_handler(client, message: Message):
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        return await message.reply_text(
            "<blockquote><b>💡 <u>ᴜsᴀɢᴇ :</u></b>\n\nʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴠɪᴅᴇᴏ ᴏʀ ᴅᴏᴄᴜᴍᴇɴᴛ ᴡɪᴛʜ <code>/extract</code> ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ɪᴛ ᴛᴏ ʜɪɢʜ-ǫᴜᴀʟɪᴛʏ ᴍᴘ3.</blockquote>"
        )

    m = await message.reply_text("<blockquote>📥 <b>ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴍᴇᴅɪᴀ ғɪʟᴇ...</b></blockquote>")

    try:
        downloaded = await message.reply_to_message.download(file_name="cache/")
        if not downloaded:
            return await m.edit_text("<blockquote>❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴇᴅɪᴀ.</b></blockquote>")

        await m.edit_text("<blockquote>⚡ <b>ᴇxᴛʀᴀᴄᴛɪɴɢ ʜɪɢʜ-ǫᴜᴀʟɪᴛʏ ᴀᴜᴅɪᴏ...</b></blockquote>")

        out_audio = f"cache/extracted_{message.id}.mp3"
        cmd = f'ffmpeg -i "{downloaded}" -vn -ar 44100 -ac 2 -b:a 320k "{out_audio}" -y'
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

        if os.path.exists(out_audio):
            await m.edit_text("<blockquote>📤 <b>ᴜᴘʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ...</b></blockquote>")
            await message.reply_audio(
                audio=out_audio,
                caption="<blockquote>🎵 <b><u>ᴀᴜᴅɪᴏ ᴇxᴛʀᴀᴄᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ</u></b>\n\n⚡ <i>ʙɪᴛʀᴀᴛᴇ : 320 ᴋʙᴘs | sᴛᴇʀᴇᴏ</i></blockquote>",
                title=f"Extracted Audio {message.id}",
                performer=app.name,
            )
            await m.delete()
            os.remove(out_audio)
        else:
            await m.edit_text("<blockquote>❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ᴇxᴛʀᴀᴄᴛ ᴀᴜᴅɪᴏ ғʀᴏᴍ ᴠɪᴅᴇᴏ.</b></blockquote>")

        if os.path.exists(downloaded):
            os.remove(downloaded)

    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>ᴇʀʀᴏʀ :</b> <code>{e}</code></blockquote>")
