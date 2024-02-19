from asyncio import Lock
from math import ceil
from pyrogram.filters import command, regex
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

from bot import LOGGER, USE_TELEGRAPH, bot, user_data
from bot.helper.ext_utils.bot_utils import sync_to_async, new_task, get_telegraph_list
from bot.helper.mirror_utils.gdrive_utils.search import gdSearch
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage


msg_dict = {}
max_total = 5
telegram_list_lock = Lock()


async def list_buttons(user_id, isRecursive=True, user_token=False):
    buttons = ButtonMaker()
    buttons.ibutton(
        "Folders", f"list_types {user_id} folders {isRecursive} {user_token}"
    )
    buttons.ibutton("Files", f"list_types {user_id} files {isRecursive} {user_token}")
    buttons.ibutton("Keduanya", f"list_types {user_id} both {isRecursive} {user_token}")
    buttons.ibutton(
        f"Recursive : {isRecursive}",
        f"list_types {user_id} rec {isRecursive} {user_token}",
    )
    buttons.ibutton(
        f"User Token : {user_token}",
        f"list_types {user_id} ut {isRecursive} {user_token}",
    )
    buttons.ibutton("Batalkan", f"list_types {user_id} cancel")
    return buttons.build_menu(2)


async def _list_drive(key, message, item_type, isRecursive, user_token, user_id):
    LOGGER.info(f"Listing: {key}")
    if user_token:
        user_dict = user_data.get(user_id, {})
        target_id = user_dict.get("gdrive_id", "") or ""
        LOGGER.info(target_id)
    else:
        target_id = ""
        
    content, contents_no = await sync_to_async(
        gdSearch(
            isRecursive=isRecursive, 
            itemType=item_type
        ).drive_list, 
        key, 
        target_id, 
        user_id
    )
    
    if content:
        if USE_TELEGRAPH:
            try:
                button = await get_telegraph_list(content)
            except Exception as e:
                await editMessage(message, e)
                return

            msg = f"<b>Menemukan</b> <code>{contents_no}</code> <b>hasil untuk kata kunci :</b>\n<code>{key}</code>"
            await editMessage(message, msg, button)
        
        else:
            msg = ""
            button = None
            
            page = 0
            page_no = 1 
            page_cur = None
            
            pages = [content for content in content for content in content.split("\n\n")]
            
            msgId = message.reply_to_message.id
            userId = (
                message.reply_to_message.from_user.id 
                or user_id
            )
            
            msg_dict[msgId] = [page, pages, page_no, page_cur, key, msgId]
            
            async with telegram_list_lock:
                page_cur = ceil(len(pages) / max_total)
                msg_dict[msgId][3] = page_cur

                if (
                    page_no > page_cur 
                    and page_cur != 0
                ):
                    page -= max_total
                    page_no -= 1

                buttons = ButtonMaker()
                
                for no, data in enumerate(pages[page:], start=1):
                    msg += "\n\n" + data
                    
                    if no == max_total:
                        break

                if len(pages) > max_total:
                    buttons.ibutton("⏪", f"tg_list {userId} pre {msgId}")
                    buttons.ibutton(f"{page_no}/{page_cur}", f"tg_list {userId} ref {msgId}")
                    buttons.ibutton("⏩", f"tg_list {userId} nex {msgId}")

                if len(pages) <= max_total:
                    buttons.ibutton(f"{page_no}/{page_cur}", f"tg_list {userId} ref {msgId}")

            buttons.ibutton("Close", f"tg_list {userId} close {msgId}", position="footer")
            await editMessage(message, msg, buttons.build_menu(3))

    else:
        await editMessage(message, f"<b>Pencarian dengan kata kunci</b> <code>{key}</code> <b>tidak ditemukan!</b>")


@new_task
async def select_type(_, query):
    user_id = query.from_user.id
    message = query.message
    key = message.reply_to_message.text.split(maxsplit=1)[1].strip()
    data = query.data.split()
    if user_id != int(data[1]):
        return await query.answer(text="Bukan Tugas darimu!", show_alert=True)
    elif data[2] == "rec":
        await query.answer()
        isRecursive = not bool(eval(data[3]))
        buttons = await list_buttons(user_id, isRecursive, eval(data[4]))
        return await editMessage(message, "<b>Pilih opsi :</b>", buttons)
    elif data[2] == "ut":
        await query.answer()
        user_token = not bool(eval(data[4]))
        buttons = await list_buttons(user_id, eval(data[3]), user_token)
        return await editMessage(message, "<b>Pilih tipe yang mau dicari :</b>", buttons)
    elif data[2] == "cancel":
        await query.answer()
        return await editMessage(message, "<b>Pencarian dibatalkan!</b>")
    await query.answer()
    item_type = data[2]
    isRecursive = eval(data[3])
    user_token = eval(data[4])
    msg = f"<b>Mencari Google Drive...</b>"
    msg += f"\n╾────────────╼\n"
    msg += f"<b>Tipe :</b> <code>{item_type.capitalize()}</code>"
    msg += f"\n<b>Recursive :</b> <code>{'Yes' if isRecursive else 'No'}</code>"
    msg += f"\n<b>User Token :</b> <code>{'Yes' if user_token else 'No'}</code>"
    msg += f"\n<b>Kata Kunci :</b> <code>{key.title()}</code>"
    msg += "\n╾────────────╼\n"
    await editMessage(message, msg)
    await _list_drive(key, message, item_type, isRecursive, user_token, user_id)


async def gdrive_search(_, message):
    if len(message.text.split()) == 1:
        return await sendMessage(message, "<b>Kirim perintah disertai dengan kata kunci!</b>")
    user_id = message.from_user.id
    buttons = await list_buttons(user_id)
    await sendMessage(message, "<b>Pilih tipe yang mau dicari :</b>", buttons)


@new_task
async def telegram_list(_, query):
    data = query.data.split()
    user_id = query.from_user.id
    
    userId = int(data[1])
    buttons = ButtonMaker()
    
    if user_id != userId:
        return await query.answer(text="Bukan Tugas darimu!", show_alert=True)

    try:
        msgs = msg_dict[int(data[3])]
    except:
        await query.message.delete()
        await query.message.reply_to_message.delete()
        return await query.answer(text="Waktu query pencarian habis!", show_alert=True)
    
    if data[2] == "pre":
        if msgs[2] == 1:
            msgs[0] = max_total * (msgs[3] - 1)
            msgs[2] = msgs[3]
        else:
            msgs[0] -= max_total
            msgs[2] -= 1
            
        msg = ""
        page_cur = ceil(len(msgs[1]) / max_total)
        
        if (
            page_cur != 0 
            and msgs[2] > page_cur
        ):
            msgs[0] -= max_total
            msgs[2] -= 1
            
        for no, data in enumerate(msgs[1][msgs[0]:], start=1):
            msg += "\n\n" + data
            if no == max_total:
                break
            
        if len(msgs[1]) > max_total:
            buttons.ibutton("⏪", f"tg_list {userId} pre {msgs[5]}")
            buttons.ibutton(f"{msgs[2]}/{page_cur}", f"tg_list {userId} ref {msgs[5]}")
            buttons.ibutton("⏩", f"tg_list {userId} nex {msgs[5]}")
            
        if len(msgs[1]) <= max_total:
            buttons.ibutton(f"{msgs[2]}/{page_cur}", f"tg_list {userId} ref {msgs[5]}")
            
        buttons.ibutton("Close", f"tg_list {userId} close {msgs[5]}", position="footer")
        await editMessage(query.message, msg, buttons.build_menu(3))
        
    elif data[2] == "nex":
        if msgs[2] == msgs[3]:
            msgs[0] = 0
            msgs[2] = 1
        else:
            msgs[0] += max_total
            msgs[2] += 1
            
        msg = ""
        page_cur = ceil(len(msgs[1]) / max_total)
        
        if (
            page_cur != 0 
            and msgs[2] > page_cur
        ):
            msgs[0] -= max_total
            msgs[2] -= 1
            
        for no, data in enumerate(msgs[1][msgs[0]:], start=1):
            msg += "\n\n" + data
            
            if no == max_total:
                break
        
        if len(msgs[1]) > max_total:
            buttons.ibutton("⏪", f"tg_list {userId} pre {msgs[5]}")
            buttons.ibutton(f"{msgs[2]}/{page_cur}", f"tg_list {userId} ref {msgs[5]}")
            buttons.ibutton("⏩", f"tg_list {userId} nex {msgs[5]}")
            
        if len(msgs[1]) <= max_total:
            buttons.ibutton(f"{msgs[2]}/{page_cur}", f"tg_list {userId} ref {msgs[5]}")
        
        buttons.ibutton("Close", f"tg_list {userId} close {msgs[5]}", position="footer")
        await editMessage(query.message, msg, buttons.build_menu(3))
    
    elif data[2] == "ref":
        await query.answer()
    
    elif data[2] == "close":
        await query.answer()
        await query.message.delete()
        await query.message.reply_to_message.delete()
        try:
            del msgs[5]
        except:
            pass
        
    else:
        await query.answer()
        for no, _ in enumerate(msgs[1], start=1):
            if no == max_total:
                break


bot.add_handler(
    MessageHandler(
        gdrive_search,
        filters=command(
            BotCommands.ListCommand
        ) & CustomFilters.authorized,
    )
)
bot.add_handler(
    CallbackQueryHandler(
        select_type, 
        filters=regex(
            "^list_types"
        )
    )
)
bot.add_handler(
    CallbackQueryHandler(
        telegram_list, 
        filters=regex(
            "^tg_list")
    )
)