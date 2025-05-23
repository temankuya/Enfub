import asyncio
import logging
from pyrogram.errors import FloodWait, Forbidden
from pyrogram.types import InlineKeyboardButton
from Kymang.modules.data import get_subs, del_sub  # Pastikan `del_sub()` berfungsi dengan benar


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def fetch_chat_info(c, sub):
    """Mengambil informasi chat secara paralel dengan pengelolaan error yang lebih baik."""
    for attempt in range(3): 
        try:
            info = await c.get_chat(sub)
            link = info.invite_link or await c.export_chat_invite_link(sub)
            return sub, link

        except FloodWait as e:
            logging.warning(f"⏳ FloodWait: Menunggu {e.value} detik sebelum melanjutkan...")
            await asyncio.sleep(e.value)

        except Exception as e:
            error_message = str(e).lower()
            logging.error(f"❌ Gagal mendapatkan info chat {sub}: {e}", exc_info=True)

            forbidden_errors = [
                "chat_write_forbidden",
                "export_chat_invite",
                "not found",
                "channel_invalid",
                "chat_admin_required",
                "no rights"
            ]
            if any(kw in error_message for kw in forbidden_errors):
                try:
                    logging.info(f"🗑️ Menghapus ID {sub} dari database...")
                    deleted = await del_sub(c.me.id, sub)
                    if deleted:
                        logging.info(f"✅ ID {sub} berhasil dihapus dari database")
                    else:
                        logging.warning(f"⚠️ ID {sub} tidak ditemukan atau gagal dihapus dari database")
                except Exception as del_error:
                    logging.error(f"❌ Gagal menghapus ID {sub} dari database: {del_error}")

            return sub, None  

    return sub, None  
    
def chunk_list(lst, n):
    """Membagi list menjadi sub-list dengan maksimal n item per sub-list."""
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def create_keyboard(links, extra_buttons=None):
    """Membuat keyboard dengan daftar link dan tombol tambahan."""
    keyboard = [InlineKeyboardButton("• Join Dulu •", url=h) for h in links]
    new_keyboard = chunk_list(keyboard, 2) 

    if extra_buttons:
        new_keyboard.append(extra_buttons)

    return new_keyboard


async def button_pas_pertama(c):
    """Membuat tombol daftar subscription."""
    subs = await get_subs(c.me.id)
    
    if not subs:
        logging.info("📌 Tidak ada subscription yang terdaftar.")
        return None

    tasks = [fetch_chat_info(c, x["sub"]) for x in subs]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Hanya ambil link yang valid (FIX: perbaikan unpacking)
    links = [result[1] for result in results if isinstance(result, tuple) and result[1]]

    if not links:
        logging.info("⚠️ Tidak ada link yang valid setelah pengecekan.")
        return None

    extra_buttons = [
        InlineKeyboardButton("Help", callback_data="cb_help"),
        InlineKeyboardButton("Close", callback_data="close"),
    ]

    return create_keyboard(links, extra_buttons)
    
async def force_button(c, m):
    """Membuat tombol untuk force subscription."""
    subs = await get_subs(c.me.id)
    if not subs:
        return None

    tasks = [fetch_chat_info(c, x["sub"]) for x in subs]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    links = [link for sub, link in results if link and not isinstance(link, Exception)]

    try:
        command_param = m.command[1] if len(m.command) > 1 else "start"
        retry_button = [
            InlineKeyboardButton(
                "Coba Lagi", url=f"https://t.me/{c.me.username}?start={command_param}"
            )
        ]
        return create_keyboard(links, retry_button)
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat membuat tombol Coba Lagi: {e}")
        return create_keyboard(links)
