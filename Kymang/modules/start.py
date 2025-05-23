import asyncio
import os
import subprocess
import sys
from datetime import datetime, timedelta
from distutils.util import strtobool
from io import BytesIO
import bson
from time import time

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from pyrogram.types import *

from Kymang import bot
from Kymang.config import *
from Kymang.modules.btn import *
from Kymang.modules.data import *
from Kymang.modules.func import *


def restart():
    os.execvp(sys.executable, [sys.executable, "-m", "Kymang"])


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60**2 * 24),
    ("hour", 60**2),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else "s"}')
    return ", ".join(parts)


start_msg = """
<blockquote>
**ʜᴀʟᴏ {}👋,

sᴀʏᴀ ᴀᴅᴀʟᴀʜ {}​ ʏᴀɴɢ ᴍᴇᴍᴘᴇʀᴍᴜᴅᴀʜ ᴋᴀʟɪᴀɴ ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴜᴀᴛ ʙᴏᴛ ғɪʟᴇ sʜᴀʀɪɴɢ ᴛᴀɴᴘᴀ ʜᴀʀᴜs ᴍᴇᴍɪʟɪᴋɪ ᴠᴘs/ʜᴇʀᴏᴋᴜ sᴇɴᴅɪʀɪ
sɪʟᴀʜᴋᴀɴ ᴋʟɪᴋ ᴛᴏᴍʙᴏʟ ᴅɪʙᴀᴡᴀʜ ɪɴɪ ᴜɴᴛᴜᴋ ᴍᴇᴍᴜʟᴀɪɴʏᴀ**
</blockquote>
"""

about_msg = """
<blockquote>
<b>**Tentang Bot ini:

{} adalah Bot Telegram untuk menyimpan Postingan atau File yang dapat diakses melalui Link Khusus.

 • Creator : {} 
 </blockquote>
"""


mbuttons = [
    [
        InlineKeyboardButton("About", callback_data="cb_about"),
        InlineKeyboardButton("Close", callback_data="close"),
    ],
]

buttons2 = [
    [
        InlineKeyboardButton("🤖 Deploy Bot", callback_data="buat_bot"),
    ],
    [
        InlineKeyboardButton("🎥 Tutorial", callback_data="cb_tutor"),
        InlineKeyboardButton("👨‍💻 Admin", callback_data="cb_admines"),
    ],
    [
        InlineKeyboardButton("🖥 Status", callback_data="cb_status"),
        InlineKeyboardButton("💌 Live Chat", callback_data="support"),
    ],
]


@bot.on_message(filters.command("start") & filters.private & subcribe)
async def start_bot(c, m):
    if c.me.id == BOT_ID:
        await add_user(c.me.id, m.from_user.id)
        await m.reply(
            start_msg.format(m.from_user.mention, c.me.mention),
            reply_markup=InlineKeyboardMarkup(buttons2),
        )
        return
    
    if await timer_info(c.me.id) == datetime.now().strftime("%d-%m-%Y"):
        print(f"@{c.me.username} telah habis, restart bot...")
        await remove_bot(str(c.me.id))
        await del_timer(c.me.id)
        asyncio.create_task(delete_files(f"{c.me.id}*"))  
        asyncio.create_task(restart())  
        return

    kon = strtobool(await protect_info(c.me.id))
    await add_user(c.me.id, m.from_user.id)

    owner_data = await cek_owner(c.me.id)
    chg = owner_data[0]["channel"] if owner_data else None
    if not chg:
        return await m.reply("⚠️ Channel tidak ditemukan di database!")

    args = m.text.split(" ", 1)
    
    if len(args) > 1:
        try:
            base64_string = args[1]
            decoded_string = await decode(base64_string)
            argument = decoded_string.split("-")
        except Exception:
            return await m.reply("⚠️ Format link tidak valid!")

        # Jika ada 3 argumen (range ID)
        if len(argument) == 3:
            try:
                start, end = int(int(argument[1]) / abs(chg)), int(int(argument[2]) / abs(chg))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))

                if any(i <= 0 for i in ids):
                    return await m.reply("ID pesan tidak valid atau tidak ditemukan.")
            except Exception:
                return await m.reply("⚠️ Format ID tidak valid!")

            temp_msg = await m.reply("__Tunggu sebentar...__")

            try:
                mes = await get_messages(c, ids)
            except Exception:
                return await temp_msg.edit("❌ Terjadi kesalahan saat mengambil pesan.")

            await temp_msg.delete()

            for msg in mes:
                if msg.empty:
                    continue  

                caption = msg.caption.html if msg.caption else ""
                try:
                    await msg.copy(
                        m.chat.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        protect_content=kon,
                        reply_markup=None,
                    )
                except FloodWait as e:
                    asyncio.create_task(asyncio.sleep(e.x))  
                    await msg.copy(
                        m.chat.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        protect_content=kon,
                        reply_markup=None,
                    )
                except Exception:
                    continue
        
        elif len(argument) == 2:
            try:
                ids = int(int(argument[1]) / abs(chg))
                if ids <= 0:
                    return await m.reply("ID pesan tidak valid atau tidak ditemukan.")
            except Exception:
                return await m.reply("⚠️ Format ID tidak valid!")

            temp_msg = await m.reply("__Tunggu sebentar...__")

            try:
                mes = await c.get_messages(chg, ids)
            except Exception:
                return await temp_msg.edit("❌ Terjadi kesalahan saat mengambil pesan.")

            caption = mes.caption.html if mes.caption else ""
            await temp_msg.delete()

            if mes.empty:
                return await m.reply("Pesan kosong atau tidak dapat disalin.")

            await mes.copy(
                m.chat.id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                protect_content=kon,
                reply_markup=None,
            )

    else:
        buttons = await button_pas_pertama(c)
        await m.reply(
            f"**Hello {m.from_user.mention}**\n\n"
            "Saya dapat menyimpan file pribadi di Channel Tertentu "
            "dan pengguna lain dapat mengaksesnya dari link khusus.",
            reply_markup=InlineKeyboardMarkup(buttons),
            )


@bot.on_message(filters.command("start") & filters.private)
async def start_bots(c, m):
    """Handler untuk perintah /start yang sudah dioptimalkan tanpa logging"""
    if c.me.id == BOT_ID:
        await add_user(c.me.id, m.from_user.id)
        buttons = await force_button(c, m)
        await m.reply(
            start_msg.format(m.from_user.mention, c.me.mention),
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
        )
        return

    av = await timer_info(c.me.id)
    time = datetime.now().strftime("%d-%m-%Y")

    if av == time:
        print(f"@{c.me.username} telah habis, restart bot...")
        await remove_bot(str(c.me.id))
        await del_timer(c.me.id)
        await delete_files(f"{c.me.id}*")
        asyncio.create_task(restart())  # Non-blocking restart
        return

    await add_user(c.me.id, m.from_user.id)
    buttons = await force_button(c, m)

    if not buttons:
        return await m.reply_text("Force-Sub kosong atau belum ada di database", quote=True)

    try:
        await m.reply(
            f"**Hello {m.from_user.mention}**\n\n"
            "Anda harus bergabung terlebih dahulu untuk melihat file yang saya bagikan.\n"
            "Silakan join ke channel terlebih dahulu.",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except Exception as e:
        print(e)


@bot.on_message(filters.command("restart") & filters.user(ADMINS))
async def restart_bot(c, m):
    try:
        update_message = await m.reply_text("🔄 Sedang memulai ulang bot....")
        await asyncio.sleep(1)
        await update_message.delete()
        await m.reply_text("**✅ BOT BERHASIL DI MULAI ULANG.**")
        return await restart()
    except Exception as e:
        await m.reply_text("⛔ Terjadi kesalahan saat memulai ulang bot.")
        await m.reply_text(str(e))


@bot.on_message(filters.command("gitpull") & filters.user(ADMINS))
async def update(client, message):
    try:
        update_message = await message.reply_text("🔄 Sedang memproses...")
        out = subprocess.check_output(["git", "pull"]).decode("UTF-8")
        if "Already up to date." in str(out):
            return await update_message.edit_text("**🤖 BOT SUDAH VERSI TERBARU!**")
        await update_message.edit_text(f"**✅ BERHASIL UPDATE BOT**\n\n```{out}```")
        return await restart()
    except Exception as e:
        await message.reply_text("⚙️ Terjadi kesalahan saat melakukan pembaruan.")
        await message.reply_text(str(e))


@bot.on_message(filters.command("id") & filters.private)
async def cek_id(c, m):
    if c.me.id != BOT_ID:
        return
    if len(m.command) < 2:
        return await m.reply_photo(
            "https://telegra.ph/file/86fff250dda1c1d9b14cb.jpg",
            caption="Silahkan kombinasikan dengan link tautan\ncontoh : /id https://t.me/AyiinChats\natau\n/id https://t.me/c/728292989/77",
        )
    link = m.command[1]
    if not "t.me" in link:
        return await m.reply("Maaf link salah")
    if "t.me/c" in link:
        try:
            chat = int("-100" + str(link.split("/")[-2]))
            await m.reply(f"**ID**: `{chat}`")
        except Exception as e:
            return await m.reply(f"**Error**: {e}")
    else:
        xx = str(link.split("/")[-1])
        try:
            chat = await c.get_chat(xx)
            await m.reply(f"**ID**: `{chat.id}`")
        except Exception as e:
            return await m.reply(f"**Error**: {e}")


@bot.on_message(
    filters.private
    & ~filters.command(
        [
            "start",
            "clone",
            "users",
            "user",
            "broadcast",
            "eval",
            "expired",
            "setdb",
            "akses",
            "setexp",
            "cekakses",
            "addadmin",
            "deladmin",
            "listadmin",
            "help",
            "del",
            "info",
            "batch",
            "addseller",
            "delseller",
            "genlink",
            "protect",
            "id",
            "addbutton",
            "delbutton",
            "listbutton",
            "ping",
            "uptime",
            "limitbutton",
        ]
    )
)
async def up_bokep(c, m):
    if c.me.id == BOT_ID:
        return
    cek = await cek_owner(c.me.id)
    adm = await admin_info(c.me.id, m.from_user.id)
    for i in cek:
        owner = i["owner"]
        dbc = i["channel"]
    av = await timer_info(c.me.id)
    time = datetime.now().strftime("%d-%m-%Y")
    if av == time:
        print(f"@{c.me.username} Telah Habis Mohon Tunggu.. Sedang Restart Bot")
        await remove_bot(str(c.me.id))
        os.popen(f"rm {c.me.id}*")
        await restart()
    if not adm and m.from_user.id != owner:
        return
    ppk = await m.reply("Tunggu sebentar...")
    iya = await m.copy(dbc)
    sagne = iya.id * abs(dbc)
    string = f"get-{sagne}"
    base64_string = await encode(string)
    link = f"https://t.me/{c.me.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Bagikan Tautan", url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )
    await ppk.edit(
        f"**Link Sharing File Berhasil Di Buat :**\n\n{link}",
        reply_markup=reply_markup,
    )
    try:
        await iya.edit_reply_markup(reply_markup)
    except Exception:
        pass


@bot.on_message(filters.command("help"))
async def helper_text(c, m):
    if c.me.id == BOT_ID:
        kymang = await cek_seller()
        if m.from_user.id in kymang:
            return await m.reply(
                """Perintah Yang Tersedia:

> - /akses : Untuk akses deploy user
> - /setexp : Untuk set masa aktif bot
> - /cekakses : Untuk cek masa aktif bot
> - /limitbutton : Untuk menentukan batas sub
> - /del : Untuk menghapus bot yang aktif"""
            )

    adm = await admin_info(c.me.id, m.from_user.id)
    kymang = await cek_seller()
    owner = await cek_owner(c.me.id)

    if not owner:
        return

    owner_id = owner[0]["owner"] if owner else None

    if m.from_user.id == owner_id:
        await c.send_message(
            m.chat.id,
            """Perintah Yang Tersedia:

> - /info : Untuk melihat masa aktif bot anda
> - /setdb : Untuk set channel base
> - /addadmin : Untuk menambahkan admin bot
> - /deladmin : Untuk menghapus admin bot
> - /listadmin : Untuk menampilkan admin
> - /users : Untuk cek pengunjung bot
> - /broadcast : Untuk kirim pesan broadcast ke pengunjung bot
> - /batch : Untuk membuat link lebih dari satu file
> - /genlink : Buat tautan untuk satu posting
> - /protect : True untuk Protect False untuk Off
> - /addbutton : Untuk menambahkan sub
> - /delbutton : Untuk menghapus sub
> - /listbutton : Untuk cek daftar fsub"""
        )

    elif adm:
        await c.send_message(
            m.chat.id,
            """Perintah Yang Tersedia:

> - /info : Untuk melihat masa aktif bot anda
> - /users : Untuk cek pengunjung bot
> - /broadcast : Untuk kirim pesan broadcast ke pengunjung bot
> - /batch : Untuk membuat link lebih dari satu file
> - /genlink : Buat tautan untuk satu posting
> - /protect : True untuk Protect False untuk Off"""
        )


@bot.on_message(
    filters.incoming
    & ~filters.command(
        [
            "del",
            "eval",
            "setdb",
            "akses",
            "user",
            "setexp",
            "addadmin",
            "deladmin",
            "listadmin",
            "expired",
            "help",
            "cekakses",
            "batch",
            "addseller",
            "delseller",
            "genlink",
            "protect",
            "id",
            "info",
            "addbutton",
            "delbutton",
            "listbutton",
            "ping",
            "uptime",
            "limitbutton",
        ]
    )
)
async def post_channel(c, m):
    if c.me.id == BOT_ID:
        return
    cek = await cek_owner(c.me.id)
    for i in cek:
        dbc = i["channel"]
    if m.chat.id != dbc:
        return
    converted_id = m.id * abs(dbc)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{c.me.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Bagikan Tautan", url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )
    try:
        await m.edit_reply_markup(reply_markup)
    except Exception:
        pass


@bot.on_message(filters.command("del") & filters.user(ADMINS))
async def del_users(c, m):
    if c.me.id != BOT_ID:
        return
    if len(m.command) < 2:
        return await m.reply("Balas pesan pengguna atau berikan ID Bot/Username Bot.")
    ids = m.command[1]
    await remove_bot(str(ids))
    await del_owner(int(ids))
    await del_timer(int(ids))
    await m.reply(f"Hapus data untuk ID {ids}")
    os.popen(f"rm {ids}*")
    return await restart()
    

@bot.on_message(filters.command("setdb"))
async def ya_setting_bot(c, m):
    if c.me.id == BOT_ID:
        return
    cek = await cek_owner(c.me.id)
    adm = await admin_info(c.me.id, m.from_user.id)
    for i in cek:
        owner = i["owner"]
    if not adm and m.from_user.id != owner:
        return
    if len(m.command) < 2:
        return await m.reply(
            "Balas pesan pengguna atau berikan user_id/username. channel database\ncontoh : /setdb -100xxxxxxx"
        )
    ids = int(m.command[1])
    try:
        await c.export_chat_invite_link(ids)
        await add_owner(int(c.me.id), int(m.from_user.id), ids)
        await m.reply(f"Channel database berhasil di set `{ids}`")
    except:
        return await m.reply(f"Maaf saya bukan admin di `{ids}`")


@bot.on_message(filters.command("akses"))
async def member_prem(c, m):
    if c.me.id != BOT_ID:
        return
    if len(m.command) < 2:
        return await m.reply(
            "Balas pesan pengguna atau berikan user_id/username.\ncontoh : /akses 5081430435"
        )
    iya = await seller_info(m.from_user.id)
    if not iya and m.from_user.id not in ADMINS:
        return
    ids = m.command[1]
    if int(ids) not in MEMBER:
        MEMBER.append(int(ids))
        await m.reply(f"{ids} Berhasil di tambahkan ke member premium")
    else:
        await m.reply(f"Maaf {ids} Sudah menjadi member premium")


@bot.on_message(filters.command("setexp"))
async def add_aktif_bot(c, m):
    if len(m.command) < 3:
        return await m.reply(
            "Balas pesan pengguna atau berikan user_id/username., 1 sama dengan 1 hari\ncontoh : /setexp 5081430435 30"
        )
    iya = await seller_info(m.from_user.id)
    if not iya and m.from_user.id not in ADMINS:
        return
    ids = m.command[1]
    h = int(m.command[2])
    time = (datetime.now() + timedelta(h)).strftime("%d-%m-%Y")
    await add_timer(int(ids), time)
    await m.reply(f"**User ID** : {ids}\n**Time** : {time}")


@bot.on_message(filters.command("cekakses"))
async def cek_member_prem(c, m):
    iya = await seller_info(m.from_user.id)
    if not iya and m.from_user.id not in ADMINS:
        return
    anu = await cek_prem()
    msg = "**Daftar member premium**\n\n"
    ang = 0
    for ex in anu:
        try:
            afa = f"`{ex['nama']}` » {ex['aktif']}"
            ang += 1
        except Exception:
            continue
        msg += f"{ang} › {afa}\n"
    await m.reply(msg)


async def cancel(callback_query, text):
    if text.startswith("/"):
        await bot.send_message(
            callback_query.from_user.id,
            "Proses di batalkan, silahkan coba lagi",
        )
        return True
    else:
        return False


async def canceled(m):
    if (
        "/cancel" in m.text
        or "/cancel" not in m.text
        and "/clone" in m.text
        or "/cancel" not in m.text
        and "/clone" not in m.text
        and m.text.startswith("/")
    ):
        await m.reply("Proses di batalkan silahkan gunakan /setting", quote=True)
        return True
    else:
        return False


@bot.on_message(filters.command("info") & filters.private)
async def status_mem(c, m):
    if c.me.id == BOT_ID:
        return
    cek = await cek_owner(c.me.id)
    for i in cek:
        owner = i["owner"]
    if m.from_user.id == int(owner):
        act = await timer_info(c.me.id)
        await c.send_message(
            int(owner),
            f"**Nama** : {c.me.first_name}\n**Id** : `{c.me.id}`\n**Experied** : {act}",
        )
    else:
        return


@bot.on_message(filters.command("ping"))
async def ping_pong(c, m):
    start = time()
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    m_reply = await m.reply("Pinging...")
    delta_ping = time() - start
    await m_reply.edit(
        "**PONG!!**🏓 \n"
        f"**• Pinger -** `{delta_ping * 1000:.3f}ms`\n"
        f"**• Uptime -** `{uptime}`\n"
    )


@bot.on_message(filters.command("uptime"))
async def get_uptime(client, m: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await m.reply_text(
        "🤖 **Bot Status:**\n"
        f"• **Uptime:** `{uptime}`\n"
        f"• **Start Time:** `{START_TIME_ISO}`"
    )


@bot.on_message(filters.command("limitbutton"))
async def add_max_bot(c, m):
    if len(m.command) < 3:
        return await m.reply("Gunakan Format /limitbutton 20731464 2")
    iya = await seller_info(m.from_user.id)
    if not iya and m.from_user.id not in ADMINS:
        return
    ids = m.command[1]
    h = int(m.command[2])
    await add_max(int(ids), h)
    await m.reply(f"**BOT_ID** : {ids}\n**Buttons** : {h}")


@bot.on_message(filters.command("user") & filters.user(OWNER_ID))
async def user(client, message):
    count = 0
    user_info = ""

    for X in bot._bot:
        try:
            expired_status = await timer_info(X.me.id)  # Cek expired dalam WIB

            count += 1
            user_info += f"""
❏ FSUB KE {count}
 ├ AKUN: {X.me.username}
 ├ ID: <code>{X.me.id}</code>
 ╰ Status: {expired_status}
"""
        except Exception as e:
            user_info += f"\n❌ Error: {str(e)}"

    if len(user_info) > 4096:
        with BytesIO(user_info.encode()) as out_file:
            out_file.name = "user_list.txt"
            await message.reply_document(document=out_file)
    else:
        await message.reply(f"<b>{user_info}</b>")

                    
