import asyncio
import importlib
import os
import sys
import traceback
from atexit import register
from sys import version as pyver

from pyrogram import __version__ as pyrover
from pyrogram import idle
from pyrogram.errors import RPCError

from Kymang import LOGGER, Bot, bot  
from Kymang.config import LOG_GRP
from Kymang.modules import loadModule
from Kymang.modules.data import get_bot, remove_bot
from Kymang.modules.plernya import plernya

msg = """
**Berhasil Di Aktifkan**
**Python Version** `{}`
**Pyrogram Version** `{}`
"""

async def auto_restart():
    while not await asyncio.sleep(43200):

        def _():
            os.system(f"kill -9 {os.getpid()} && python3 -m Kymang")

        register(_)
        sys.exit(0)

async def main():
    try:
        await bot.start()
        LOGGER("Info").info("🚀 Bot utama berhasil dimulai!")

        for bt in await get_bot():
            b = Bot(**bt)
            try:
                await b.start()
                LOGGER("Info").info(f"✅ {b.me.first_name} [Berhasil Diaktifkan]")
            except RPCError:
                await remove_bot(bt["name"])
                LOGGER("Warning").warning(f"⚠️ {bt['name']} dihapus dari database karena gagal diaktifkan.")

        for mod in loadModule():
            try:
                importlib.reload(importlib.import_module(f"Kymang.modules.{mod}"))
                LOGGER("Info").info(f"✅ Module {mod} berhasil dimuat!")
            except Exception as e:
                error_detail = traceback.format_exc()
                LOGGER("Error").error(f"❌ Gagal memuat module {mod}: {e}\n{error_detail}")

        LOGGER("Info").info(f"[🤖 @{bot.me.first_name} 🤖] [🔥 BERHASIL DIAKTIFKAN! 🔥]")
        await bot.send_message(LOG_GRP, msg.format(pyver.split()[0], pyrover))

        await plernya()
        await auto_restart()
        await idle()
    except Exception as e:
        error_detail = traceback.format_exc()
        LOGGER("Error").error(f"🚨 Terjadi error saat menjalankan bot: {e}\n{error_detail}")

if __name__ == "__main__":
    LOGGER("Info").info("🛠️ Memulai bot...")
    
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except Exception as e:
        error_detail = traceback.format_exc()
        LOGGER("Error").error(f"❌ Bot gagal dimulai: {e}\n{error_detail}")
