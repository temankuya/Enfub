import subprocess
import sys
import traceback
from io import BytesIO, StringIO
from os import execvp
from sys import executable

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from meval import meval 

from Kymang import bot
from Kymang.config import ADMINS


async def restart():
    execvp(executable, [executable, "-m", "Kymang"])


@bot.on_message(filters.command("update"))
async def update_handler(_, message):
    try:
        out = subprocess.check_output(["git", "pull"]).decode("UTF-8")
        if "Already up to date." in out:
            return await message.reply_text("It's already up-to-date!")
        await message.reply_text(f"```{out}```")
    except Exception as e:
        return await message.reply_text(str(e))
    await message.reply_text("**Updated with default branch, restarting now.**")
    await restart()


@bot.on_message(filters.user(ADMINS) & filters.command("meval"))
async def meval_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("Please provide code to execute.")
    
    cmd = message.text.split(" ", maxsplit=1)[1]
    status_message = await message.reply_text("Processing ...")
    reply_to_ = message.reply_to_message or message

    try:
        result = await meval(cmd, globals(), **{"client": client, "message": message})
        output = str(result) if result is not None else "Success"
    except Exception as e:
        output = traceback.format_exc()

    final_output = f"**MEVAL**: `{cmd}`\n\n**OUTPUT**:\n`{output.strip()}`"

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📋 Salin", callback_data=f"copy|{output.strip()}")]]
    )

    if len(final_output) > 4096:
        with BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "meval.txt"
            await reply_to_.reply_document(
                document=out_file,
                caption=cmd[: 4096 // 4 - 1],
                disable_notification=True,
                quote=True,
            )
    else:
        await reply_to_.reply_text(final_output, quote=True, reply_markup=keyboard)
    
    await status_message.delete()


@bot.on_callback_query(filters.regex(r"copy\|(.+)"))
async def copy_callback(client, callback_query):
    output_text = callback_query.data.split("|", maxsplit=1)[1]
    try:
        await callback_query.message.reply(output_text)
        await callback_query.answer("Teks disalin! 📋", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)
