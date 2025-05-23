import asyncio
import importlib
import contextlib
import logging
import os

from datetime import datetime, timedelta
from pykeyboard import InlineKeyboard
from pyrogram import Client, filters, types, errors
from pyrogram.types import *

from Kymang import Bot, bot
from Kymang.config import *
from Kymang.modules import loadModule
from Kymang.modules.btn import *
from Kymang.modules.data import *
from Kymang.modules.func import *


from .start import (
    buttons2,
    cancel,
    start_msg,
    about_msg,
    mbuttons
)

lonte = []


logs = logging.getLogger(__name__)


info = {}


order_bttn = types.InlineKeyboardMarkup(
    [
        [
            types.InlineKeyboardButton('-1 Bulan', callback_data='minus.duration'),
            types.InlineKeyboardButton('+1 Bulan', callback_data='plus.duration'),
        ],
        [
            types.InlineKeyboardButton(
                '🔙 Kembali',
                callback_data='back_start',
            ),
            types.InlineKeyboardButton('🚀 Lanjutkan', callback_data='pay.pay'),
        ],
    ]
)


@bot.on_callback_query(filters.regex("cb_admines"))
async def _(_, query: CallbackQuery):
    return await query.edit_message_text(
        """
    <b> 💌 Silakan Hubungi Admin Dibawah Jika Anda Membutuhkan Bantuan.</b>""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="👨‍💻 Admin", user_id=843830036),
                ],
                [
                    InlineKeyboardButton(
                        "Back", callback_data="back_start"),
                ],
            ]
        ),
    )

@bot.on_callback_query(filters.regex("cb_help"))
async def _(_, query: CallbackQuery):
    return await CallbackQuery.edit_message_text("""<b>
    **❏ Perintah Untuk Admin Bot.
    ├/info - Untuk melihat masa aktif bot anda
    ├/setdb - Untuk mengatur channel database anda
    ├/addadmin - Untuk menambahkan admin bot
    ├/deladmin - Untuk menghapus admin bot
    ├/listadmin - Untuk menampilkan daftar admin
    ├/users - Untuk cek pengguna bot
    ├/broadcast - Untuk kirim pesan broadcast 
    ├/batch - Untuk membuat link lebih dari satu file
    ├/genlink - Untuk buat tautan untuk satu posting
    ├/protect -  Untuk privasi konten anda
    ├/addbutton - Untuk menambahkan tombol
    ├/delbutton - Untuk menghapus tombol
    └/listbutton - Untuk melihat daftar tombol**</b>""",
    reply_markup=InlineKeyboardMarkup(mbuttons),
    )


@bot.on_callback_query(filters.regex("cb_about"))
async def _(c: Client, query: CallbackQuery):
    ownerObj = (await cek_owner(c.me.id))[0]
    owner = ownerObj["owner"]
    try:
        user = await c.get_users(owner)
    except BaseException as a:
        print(a)
        return
    await query.message.edit(
        about_msg.format(c.me.mention, user.mention),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Back", callback_data="bck_cb"),
                ],
            ]
        ),
    )
                 

@bot.on_callback_query(filters.regex("cb_tutor"))
async def _(_, callback_query: CallbackQuery):
    await callback_query.message.edit(
        text="**Berikut adalah video tutorial\n**Gabung Channel dibawah ini untuk melihat tutorial!**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🎥 Tutorial", url="https://t.me/TutorialDeploy"
                    ),
                ],
                [
                    InlineKeyboardButton("Back", callback_data="back_start"),
                ],
            ]
        ),
    )




@bot.on_callback_query(filters.regex("cb_status"))
async def _(_, callback_query: CallbackQuery):
    anu = await cek_prem()
    status_text = ""
    for ex in anu:
        try:
            afa = f"`{ex['nama']}` » {ex['aktif']}"
            status_text += f"{afa}\n"
        except Exception as e:
            print(f"Error: {e}")

    text_to_send = "❌ Bot belum aktif"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Back", callback_data="back_start"),
            ],
        ]
    )
    await callback_query.message.edit(
        text=text_to_send,
        reply_markup=reply_markup,
    )


@bot.on_callback_query(filters.regex('via_bot'))
async def order_bot_handler(_, cb: types.CallbackQuery):
    user = cb.from_user
    text = """🛒 Order Bot Fsub Premium

Jumlah Order: {jumlah} bulan

Harga: Rp. {harga} / bulan"""
    if info.get(user.id):
        data = info[user.id]
        text += """
Diskon: Rp. {discount:,.0f}
Total: Rp. {total:,.0f} (-10%)"""
    else:
        data = {
            'jumlah': 1,
            'harga': 40_000,
            'discount': 0,
            'total': 40_000,
        }
        info[user.id] = data
        text += '\nTotal: Rp. {total:,.0f}'
    text = text.format(**data)
    text = text.replace(',', '.')
    return await cb.message.edit(
        text,
        reply_markup=order_bttn,
    )



@bot.on_callback_query(filters.regex(r'(plus|minus).duration'))
async def plus_minus_handler(_, cb: types.CallbackQuery):
    user = cb.from_user
    if data := info.get(user.id):
        jumlah = data['jumlah']
    else:
        jumlah = 1
        data = {
            'jumlah': jumlah,
            'harga': 40_000,
            'discount': 0,
            'total': 40_000,
        }
        info[user.id] = data
    if cb.matches[0].group(1) == 'plus':
        jumlah += 1
    else:
        jumlah -= 1
    if jumlah < 1:
        jumlah = 1
    data['jumlah'] = jumlah
    harga = data['harga'] * jumlah
    text = "🛒 Order Bot Fsub Premium\n\n"
    text += f"Jumlah Order: {data['jumlah']} bulan\n\n"
    text += "Harga: Rp. 40.000 / bulan\n"
    if jumlah > 1:
        total = data['total'] = harga - (harga*10/100)
        diskon = data['discount'] = harga - total
        text += f"Diskon: Rp. {diskon:,.0f}\n"
    else:
        total: data['total'] = harga
    mark = '(-10%)' if jumlah > 1 else ''
    text += f"Total: Rp. {total:,.0f} {mark}"
    text = text.replace(',', '.')
    with contextlib.suppress(errors.MessageNotModified):
        return await cb.message.edit(text, reply_markup=order_bttn)



@bot.on_callback_query(filters.regex('pay.(pay|e-wallet|bca|qris)'))
async def payment_handlers(c, cb: types.CallbackQuery):
    tipe = cb.matches[0].group(1)
    if tipe == 'pay':
        return await cb.message.edit(
            "💰 Silahkan pilih metode pembayaran yang ingin anda gunakan",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton("💳 Via E-wallet💳", callback_data="pay.e-wallet"),
                        types.InlineKeyboardButton("💳 Via BCA 💳", callback_data="pay.bca"),
                    ],
                    [types.InlineKeyboardButton("💳 Via Qris 💳", callback_data="pay.qris")],
                    [types.InlineKeyboardButton("🔙 Kembali", callback_data="back_start")],
                ]
            ),
        )
    else:
        if not (data := info.get(cb.from_user.id)):
            return await cb.answer(
                "Terjadi kesalahan\nSilakan mulai dari awal", show_alert=True
            )
        text = f"""💰{tipe.upper()}
Untuk mengirim pembayaran melalui {tipe.upper()} gunakan nomor tujuan berikut:

{tipe.upper()}: {payment_nomor[tipe]}
a/n: {payment_name[tipe]}

Setelah anda melakukan pembayaran,
tekan tombol dibawah ini untuk melakukan konfirmasi
Total Harga: Rp {data["total"]:,.0f}"""
        text = text.replace(",", ".")
        return await cb.message.edit(
            text,
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(
                            "📤 Konfirmasi 📤",
                            callback_data=f"bukti.{tipe}.{cb.from_user.id}",
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            "🔙 Kembali",
                            callback_data="pay.pay",
                        )
                    ],
                ]
            ),
        )


@bot.on_callback_query(filters.regex(r'(bukti|acc|rej).(e-wallet|dana|bca|qris).(\d+)'))
async def confirm_handler(c: Client, cb: types.CallbackQuery):
    tipe = cb.matches[0].group(1)  
    pay = cb.matches[0].group(2)  
    user_id = int(cb.matches[0].group(3))  
    admin_id = cb.from_user.id  

    data = info.get(user_id)
    if not data:
        return await cb.answer("Data tidak ditemukan.", show_alert=True)

    if tipe == 'bukti':
        with contextlib.suppress(Exception):
            await cb.message.delete()
        
        bukti = await c.ask(
            user_id,
            f'Silakan kirimkan bukti pembayaran {pay.upper()} yang sudah Anda lakukan',
            filters=filters.photo,
        )
        caption = bukti.caption or ''

        await bukti.copy(
            LOG_GRP,
            caption=f'\n\nPembayaran: {pay.upper()}\nDurasi: {data["jumlah"]} Bulan\nHarga: {data["total"]}\n\n{caption}',
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [types.InlineKeyboardButton('UserLink', url=f"tg://user?id={user_id}")],
                    [
                        types.InlineKeyboardButton('Terima ✅', callback_data=f'acc.{pay}.{user_id}'),
                        types.InlineKeyboardButton('Tolak ❌', callback_data=f'rej.{pay}.{user_id}')
                    ]
                ]
            )
        )
        return await cb.message.reply('Bukti pembayaran Anda telah dikirimkan. Tunggu konfirmasinya...')

    elif tipe in ['acc', 'rej']:
        is_seller = admin_id in await cek_seller()
        is_owner = await cek_owner(admin_id)

        if not is_seller and not is_owner:
            return await cb.answer("Anda tidak memiliki izin untuk menyetujui atau menolak pembayaran.", show_alert=True)

        if tipe == 'acc':
            if user_id not in MEMBER:
                MEMBER.append(user_id)

            time = data['jumlah']
            time = (datetime.now() + timedelta(days=time * 30)).strftime("%d-%m-%Y")

            await add_timer(user_id, time)

            await aktifdb.update_one(
                {"_id": user_id},
                {"$set": {"status": "active"}}
            )

            await cb.message.edit('✅ Pengguna telah disetujui.')
            return await c.send_message(user_id, f'Selamat! Anda telah diberi akses ke pembuatan bot Fsub hingga {time}.')

        else: 
            await cb.message.edit('❌ Pengguna telah ditolak.')
            return await c.send_message(user_id, 'Mohon maaf, permintaan pembelian bot Anda ditolak.')
            
@bot.on_callback_query(filters.regex("back_start"))
async def back_start_bc(c, callback_query: CallbackQuery):
    await callback_query.message.edit(
        start_msg.format(callback_query.from_user.mention, c.me.mention),
        reply_markup=InlineKeyboardMarkup(buttons2),
    )


@bot.on_callback_query(filters.regex("buat_bot"))
async def _(c, callback_query: CallbackQuery):
    if c.me.id != BOT_ID:
        return
    user_id = callback_query.from_user.id
    kymang = await cek_seller()
    if user_id not in MEMBER and user_id not in kymang:
        await callback_query.message.edit(
            "**🤖 Buat Fsub Bot**\n\n**Untuk mengakses fitur Premium ini, Anda perlu melakukan pembelian.**\n**Beli sekarang untuk bisa membuat Bot Fsub Premium!**",
            reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="👨‍💻 Admin", user_id=843830036),
                    InlineKeyboardButton(text="Via Bot", callback_data="via_bot"),
                ],
                [
                    InlineKeyboardButton(
                        "Back", callback_data="back_start"
                    ),
                ],
            ]
        ),
    )
        return
    await callback_query.message.delete()
    api_id = await c.ask(
        user_id,
        "**Dapatkan API ID di web my.telegram.org**\n\n**Silahkan masukan API_ID**",
        filters=filters.text,
    )
    if await cancel(callback_query, api_id.text):
        return
    try:
        api_ids = int(api_id.text)
    except ValueError:
        await api_id.reply(
            "**API ID Haruslah berupa angka.**",
            quote=True,
        )
        return
    api_hash = await c.ask(
        user_id,
        "**Dapatkan API HASH di web my.telegram.org**\n**Silahkan masukan API_HASH**",
        filters=filters.text,
    )
    if await cancel(callback_query, api_hash.text):
        return
    bot_token = await c.ask(
        user_id,
        "**Dapatkan dari @BotFather**\n**Silahkan masukan BOT TOKEN**",
        filters=filters.text,
    )
    if await cancel(callback_query, bot_token.text):
        return
    name_id = bot_token.text.split(":")[0]
    mang = Bot(
        name=str(name_id),
        api_id=api_ids,
        api_hash=api_hash.text,
        bot_token=bot_token.text,
    )
    try:
        mang.in_memory = False
        await mang.start()

        await c.send_message(
            user_id,
            f"**🤖 Bot Ditemukan:**\n**• Nama :** {mang.me.mention}\n**• ID :** `/setexp {mang.me.id} 365`\n**• Username :** @{mang.me.username}",
        )
    except Exception as e:
        return await c.send_message(user_id, f"**ERROR**:\n{e}")
    channel_id = await c.ask(
        user_id,
        "**Masukan ID Channel Untuk Database,\n\Pastikan Bot sudah menjadi admin di Channel Database\nContoh -100xxxx**",
        filters=filters.text,
    )
    if await cancel(callback_query, channel_id.text):
        return
    try:
        await mang.export_chat_invite_link(int(channel_id.text))
        await channel_id.reply(f"Channel Database Ditemukan `{channel_id.text}`", quote=True)
    except Exception:
        channel_id = await c.ask(user_id,
            f"Pastikan @{mang.me.username} adalah admin di Channel Database tersebut.\n\n Channel Database : `{channel_id.text}`\n\nMohon Masukkan Ulang !",
            filters=filters.text,
        )

    sub_id = await c.ask(
        user_id,
        "**Silakan Masukkan ID Channel Atau Grup Sebagai Force Subscribe !\n\nDan Pastikan Bot Anda Adalah Admin Di Grup/Channel Tersebut.**",
    )
    if await cancel(callback_query, sub_id.text):
        return
    try:
        if int(sub_id.text) != 0:
            await mang.export_chat_invite_link(int(sub_id.text))
            await sub_id.reply(f"Force-Subs terdeteksi `{sub_id.text}`", quote=True)
    except Exception:
        sub_id = await c.ask(user_id,
            f"Pastikan @{mang.me.username} adalah admin di Channel atau Group tersebut.\n\n Channel atau Group Saat Ini: `{sub_id.text}`\n\nMohon Masukkan Ulang !",
            filters=filters.text,
        )
    admin_id = await c.ask(
        user_id,
        "**Silakan Masukan ID Admin Untuk Bot Anda !**",
        filters=filters.text,
    )
    if await cancel(callback_query, admin_id.text):
        return
    try:
        admin_ids = int(admin_id.text)
    except ValueError:
        admin_id = await c.ask(user_id,
            "Bukan ID Pengguna Yang Valid, ID Pengguna Haruslah Berupa Integer",
            filters=filters.text,
        )
    owner_id = await c.ask(
        user_id,
        "**Silakan Masukan ID Owner Untuk Bot Anda !**",
        filters=filters.text,
    )
    if await cancel(callback_query, owner_id.text):
        return
    try:
        owner_ids = int(owner_id.text)
    except ValueError:
        owner_id = await c.ask(user_id,
            "Bukan ID Pengguna Yang Valid, ID Pengguna Haruslah Berupa Integer",
            filters=filters.text,
        )
    await c.send_message(user_id, "**Sukses Di Deploy . Silakan Tunggu Sebentar...**")
    await add_bot(str(mang.me.id), api_ids, api_hash.text, bot_token.text)
    await add_owner(mang.me.id, owner_ids, int(channel_id.text))
    await add_admin(mang.me.id, admin_ids)
    await add_sub(
        mang.me.id,
        int(sub_id.text),
    )
    time = (datetime.now() + timedelta(30)).strftime("%d-%m-%Y")
    await add_timer(mang.me.id, time)
    anu = await c.send_message(
        LOG_GRP,
        f"**• Nama** : {mang.me.first_name}\n**• Username** : @{mang.me.username}\n**Id**: {mang.me.id}\n**• Masa Aktif** : {time}\n\n**• Pembuat**: {callback_query.from_user.mention}\n**• Id Pengguna**: {callback_query.from_user.id}",
    )

    await c.pin_chat_message(LOG_GRP, anu.id)
    sinting = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Bot Aktif", callback_data=f"telah_aktif {callback_query.from_user.id} {mang.me.username}"
                )
            ]
        ]
    )
    await c.send_message(LOG_GRP, f"Pesan untuk deployer @{mang.me.username}", reply_markup=sinting
    )
    os.popen(f"rm {name_id}*")
    for mod in loadModule():
            importlib.reload(importlib.import_module(f"Kymang.modules.{mod}"))
    await c.send_message(user_id, "**Bot Fsub Anda Sudah Aktif Dan Bisa Langsung Digunakan !\n\nKetik /help Di Bot Anda Untuk Melihat Perintah Yang Tersedia .\n\nTerima Kasih ...**")


@bot.on_callback_query(filters.regex("support"))
async def _(c, callback_query: CallbackQuery):
    user_id = int(callback_query.from_user.id)
    full_name = f"{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}"
    try:
        buttons = [
            [InlineKeyboardButton("❌ Batal", callback_data=f"batal {user_id}")]
        ]
        pesan = await c.ask(
            user_id,
            "Kirimkan Pesan Anda, Admin akan membalas Pesan anda secepatnya.",
            reply_markup=InlineKeyboardMarkup(buttons),
            timeout=60,
        )
        await c.send_message(
            user_id, "✅ Pesan Anda Telah Dikirim Ke Admin, Silahkan Tunggu Balasannya"
        )
        await callback_query.message.delete()
    except asyncio.TimeoutError:
        return await c.send_message(user_id, "**Pembatalan otomatis**")
    button = [
        [
            InlineKeyboardButton(full_name, user_id=user_id),
            InlineKeyboardButton("💌 Jawab", callback_data=f"jawab_pesan {user_id}"),
        ],
    ]
    await pesan.copy(
        LOG_GRP,
        reply_markup=InlineKeyboardMarkup(button),
    )


@bot.on_callback_query(filters.regex("jawab_pesan"))
async def _(c, callback_query: CallbackQuery):
    user_id = int(callback_query.from_user.id)
    user_ids = int(callback_query.data.split()[1])
    full_name = f"{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}"
    if user_ids == LOG_GRP:
        try:
            button = [
                [InlineKeyboardButton("Batal", callback_data=f"batal {user_id}")]
            ]
            pesan = await c.ask(
                user_id,
                "Silahkan Kirimkan Balasan Anda.",
                reply_markup=InlineKeyboardMarkup(button),
                timeout=60,
            )
            await c.send_message(
                user_id,
                "✅ Pesan Anda Telah Dikirim Ke Admin, Silahkan Tunggu Balasannya",
            )
            await callback_query.message.delete()
        except asyncio.TimeoutError:
            return await c.send_message(user_id, "**❌ Pembatalkan otomatis**")
        buttons = [
            [
                InlineKeyboardButton(full_name, user_id=user_id),
                InlineKeyboardButton("Jawab", callback_data=f"jawab_pesan {user_id}"),
            ],
        ]
    else:
        try:
            button = [
                [InlineKeyboardButton("Batal", callback_data=f"batal {LOG_GRP}")]
            ]
            pesan = await c.ask(
                LOG_GRP,
                "💌 Silahkan Kirimkan Balasan Anda.",
                reply_markup=InlineKeyboardMarkup(button),
                timeout=60,
            )
            await c.send_message(
                LOG_GRP,
                "✅ Pesan Anda Telah Dikirim Ke User, Silahkan Tunggu Balasannya",
            )
            await callback_query.message.delete()
        except asyncio.TimeoutError:
            return await c.send_message(LOG_GRP, "**Pembatalkan otomatis**")
        buttons = [
            [
                InlineKeyboardButton("💌 Jawab", callback_data=f"jawab_pesan {LOG_GRP}"),
            ],
        ]

    await pesan.copy(
        user_ids,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@bot.on_callback_query(filters.regex("batal"))
async def _(client, callback_query: CallbackQuery):
    user_ids = int(callback_query.data.split()[1])
    if user_ids == LOG_GRP:
        client.cancel_listener(LOG_GRP)
        await client.send_message(LOG_GRP, "**❌ Pesan di batalkan**")
    else:
        client.cancel_listener(user_ids)
        await client.send_message(user_ids, "**❌ Pesan di batalkan**")
    await callback_query.message.delete()
    return True


@bot.on_callback_query(filters.regex("bck_cb"))
async def _(c, query: CallbackQuery):
    buttons = await button_pas_pertama(c)
    await query.message.edit(
            f"**Hello {query.from_user.mention}**\n\n**Saya dapat menyimpan file di Channel Tertentu dan pengguna lain dapat mengaksesnya dari link khusus.**",
            reply_markup=InlineKeyboardMarkup(buttons),
    )


@bot.on_callback_query(filters.regex("telah_aktif"))
async def _(client, callback_query: CallbackQuery):
    user_ids = int(callback_query.data.split()[1])
    bot_user = callback_query.data.split()[2]
    await client.send_message(user_ids, f"✅ Bot kamu telah aktif silahkan start bot @{bot_user}")
    await callback_query.message.edit("**✅ Pesan telah di kirim**")


@bot.on_callback_query(filters.regex("close"))
async def cb_close(c, query: CallbackQuery):
    try:
        await query.answer()
        await query.message.delete()
    except BaseException as e:
        logs.info(e)
