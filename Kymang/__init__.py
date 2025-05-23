import asyncio
import sys
from pyrogram import Client
from pyrogram.handlers.message_handler import MessageHandler
from pyrogram.handlers.callback_query_handler import CallbackQueryHandler
from pyromod import listen

from Kymang.config import API_HASH, API_ID, BOT_TOKEN, MONGO_URL
from Kymang.modules.data import mongo_client
from .logging import LOGGER


for var, name in [(API_ID, "API_ID"), (API_HASH, "API_HASH"), (BOT_TOKEN, "BOT_TOKEN"), (MONGO_URL, "MONGO_URL")]:
    if not var:
        print(f"{name} Tidak ada")
        sys.exit()


class Bot(Client):
    __module__ = "pyrogram.client"
    _bot = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_message(self, filters=None):
        def decorator(func):
            if not self._bot:
                print("⚠️ Tidak ada bot instance yang aktif!")
                return func
            for ub in self._bot:
                ub.add_handler(MessageHandler(func, filters))
            return func

        return decorator

    def on_callback_query(self, filters=None):
        def decorator(func):
            if not self._bot:
                print("⚠️ Tidak ada bot instance yang aktif!")
                return func
            for ub in self._bot:
                ub.add_handler(CallbackQueryHandler(func, filters))
            return func

        return decorator

    async def start(self):
        await super().start()
        if self not in self._bot:
            self._bot.append(self)
        print(f"✅ Bot {self.name} berhasil dimulai!")

        try:
            mongo_client.server_info()
            print("✅ Koneksi MongoDB berhasil!")
        except Exception as e:
            print(f"❌ Gagal terhubung ke MongoDB: {e}")
            sys.exit(1)


bot = Bot(
    name="Botsub",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    )
