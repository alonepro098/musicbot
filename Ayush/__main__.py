import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Music Bot is running!')

    def log_message(self, format, *args):
        pass

def start_render_health_server():
    port = int(os.environ.get('PORT', 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f'[RENDER] Health web server running on port {port}')
        server.serve_forever()
    except Exception as e:
        print(f'[RENDER ERROR] Failed to bind port {port}: {e}')

threading.Thread(target=start_render_health_server, daemon=True).start()

import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Ayush import LOGGER, app, userbot
from Ayush.core.call import Aayu
from Ayush.misc import sudo
from Ayush.plugins import ALL_MODULES
from Ayush.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("Ayush.plugins" + all_module)
    LOGGER("Ayush.plugins").info("sᴜᴄᴄᴇssғᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ᴀʟʟ ᴍᴏᴅᴜʟᴇs...")
    await userbot.start()
    await Aayu.start()
    try:
        await Aayu.stream_call("https://files.catbox.moe/slt3lk.mp4")
    except NoActiveGroupCall:
        LOGGER("Ayush").error(
            "Please turn on the videochat of your log group\\channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass
    await Aayu.decorators()
    LOGGER("Ayush").info(
        "ᴍᴜsɪᴄ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("Ayush").info("ʙᴏᴛ sʜᴜᴛᴅᴏᴡɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
