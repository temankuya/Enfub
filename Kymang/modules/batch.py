from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Kymang import bot
from Kymang.config import *
from Kymang.modules.data import *
from Kymang.modules.func import *


@bot.on_message(filters.private & filters.command("batch"))
async def batch(client, message):
    if client.me.id == BOT_ID:
        return
    cek = await cek_owner(client.me.id)
    adm = await admin_info(client.me.id, message.from_user.id)
    owner, chg = None, None
    for i in cek:
        owner = i["owner"]
        chg = i["channel"]

    if not adm and message.from_user.id != owner:
        return

    while True:
        try:
            first_message = await client.ask(
                message.from_user.id,
                "<b>Silahkan Teruskan Pesan/File Pertama dari Channel Database. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        await first_message.reply(
            "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>",
            quote=True,
        )

    while True:
        try:
            second_message = await client.ask(
                message.from_user.id,
                "<b>Silahkan Teruskan Pesan/File Terakhir dari Channel DataBase. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        await second_message.reply(
            "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>",
            quote=True,
        )

    string = f"get-{f_msg_id * abs(chg)}-{s_msg_id * abs(chg)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.me.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Bagikan Tautan", url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )
    await second_message.reply_text(
        f"<b>Link Sharing File Berhasil Di Buat:</b>\n\n{link}",
        quote=True,
        reply_markup=reply_markup,
    )


@bot.on_message(filters.private & filters.command("genlink"))
async def link_generator(client, message):
    if client.me.id == BOT_ID:
        return
    cek = await cek_owner(client.me.id)
    adm = await admin_info(client.me.id, message.from_user.id)
    owner, chg = None, None
    for i in cek:
        owner = i["owner"]
        chg = i["channel"]

    if not adm and message.from_user.id != owner:
        return

    while True:
        try:
            channel_message = await client.ask(
                message.from_user.id,
                "<b>Silahkan Teruskan Pesan dari Channel DataBase. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except Exception:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        await channel_message.reply(
            "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>",
            quote=True,
        )

    base64_string = await encode(f"get-{msg_id * abs(chg)}")
    link = f"https://t.me/{client.me.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Bagikan Tautan", url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )
    await channel_message.reply_text(
        f"<b>Link File Sharing Berhasil Di Buat:</b>\n\n{link}",
        quote=True,
        reply_markup=reply_markup,
    )
