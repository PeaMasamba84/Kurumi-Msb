#!/usr/bin/env python3
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import bot, LOGGER
from bot.helper.mirror_utils.gdrive_utlis.count import gdCount
from bot.helper.telegram_helper.message_utils import deleteMessage, sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.ext_utils.bot_utils import is_gdrive_link, sync_to_async, new_task, get_readable_file_size


@new_task
async def countNode(_, message):
    args = message.text.split()
    if username := message.from_user.username:
        tag = f"@{username}"
    else:
        tag = message.from_user.mention

    link = args[1] if len(args) > 1 else ''
    if len(link) == 0 and (reply_to := message.reply_to_message):
        if reply_to.text:
            link = reply_to.text.split(maxsplit=1)[0].strip()
            if not is_gdrive_link(link) and reply_to.reply_markup:
                try:
                    link = reply_to.reply_markup.inline_keyboard[0][0].url
                except:
                    link = reply_to.reply_markup.inline_keyboard[0].url
    if is_gdrive_link(link):
        msg = await sendMessage(message, f"<b>Menghitung :</b>\n<code>{link}</code>")
        name, mime_type, size, files, folders = await sync_to_async(gdCount().count, link, message.from_user.id)
        await deleteMessage(msg)
        if mime_type is None:
            await sendMessage(message, name)
            return
        msg = f'<b>Nama :</b> <code>{name}</code>'
        msg += f'\n\n<b>Ukuran :</b> <code>{get_readable_file_size(size)}</code>'
        msg += f'\n\n<b>Tipe :</b> <code>{mime_type}</code>'
        if mime_type == 'Folder':
            msg += f'\n\n<b>Sub Folders :</b> <code>{folders}</code>'
            msg += f'\n\n<b>Files :</b> <code>{files}</code>'
        msg += f'\n\n<b>Oleh :</b> {tag}'
    else:
        msg = '<b>Kirim perintah dengan Link Google Drive atau balas Link Google Drive dengan perintah!</b>'
    await sendMessage(message, msg)


bot.add_handler(MessageHandler(countNode, filters=command(
    BotCommands.CountCommand) & CustomFilters.authorized))