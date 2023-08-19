#!/usr/bin/env python3
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from bot import bot, LOGGER
from bot.helper.telegram_helper.message_utils import auto_delete_message, sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.gdrive_utlis.delete import gdDelete
from bot.helper.ext_utils.bot_utils import is_gdrive_link, sync_to_async, new_task


@new_task
async def deletefile(_, message):
    args = message.text.split()
    if len(args) > 1:
        link = args[1]
    elif reply_to := message.reply_to_message:
        if reply_to.text:
            link = reply_to.text.split(maxsplit=1)[0].strip()
            if not is_gdrive_link(link) and reply_to.reply_markup:
                try:
                    link = reply_to.reply_markup.inline_keyboard[0][0].url
                except:
                    link = reply_to.reply_markup.inline_keyboard[0].url
    else:
        link = ''
    if is_gdrive_link(link):
        LOGGER.info(link)
        msg = await sync_to_async(gdDelete().deletefile, link, message.from_user)
    else:
        msg = '<b>Kirim perintah dengan Link Google Drive atau balas Link Google Drive dengan perintah!</b>'
    reply_message = await sendMessage(message, msg)
    await auto_delete_message(message, reply_message)


bot.add_handler(MessageHandler(deletefile, filters=command(
    BotCommands.DeleteCommand) & CustomFilters.sudo))
