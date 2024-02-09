from psutil import (
    cpu_percent, 
    virtual_memory, 
    disk_usage, 
    net_io_counters
)
from pyrogram.filters import command, regex
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from time import time

from bot import (
    task_dict_lock,
    status_dict,
    task_dict,
    botStartTime,
    DOWNLOAD_DIR,
    Intervals,
    bot,
)
from bot.helper.ext_utils.bot_utils import new_task, sync_to_async
from bot.helper.ext_utils.status_utils import (
    MirrorStatus,
    get_readable_file_size,
    get_readable_time,
    speed_string_to_bytes,
)
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import (
    sendMessage,
    deleteMessage,
    auto_delete_message,
    sendStatusMessage,
    update_status_message,
)


@new_task
async def mirror_status(_, message):
    async with task_dict_lock:
        count = len(task_dict)
    if count == 0:
        msg = "<b>Kosong bro!</b>"
        msg += f"\n\n<b>Note :</b>\nTambahkan <code>me</code> atau <code>userId</code> setelah perintah untuk menampilkan Tugas secara spesifik!"
        msg += "\n___________________________"
        msg += (
            f"\n<b>CPU :</b> <code>{cpu_percent()}%</code> | <b>FREE :</b> <code>{get_readable_file_size(disk_usage(DOWNLOAD_DIR).free)}</code>" \
            f"\n<b>RAM :</b> <code>{virtual_memory().percent}%</code> | <b>UPTIME :</b> <code>{get_readable_time(time() - botStartTime)}</code>" \
            f"\n<b>T.Unduh :</b> <code>{get_readable_file_size(net_io_counters().bytes_recv)}</code> | <b>T. Unggah :</b> <code>{get_readable_file_size(net_io_counters().bytes_sent)}</code>"  
        )
        reply_message = await sendMessage(message, msg)
        await auto_delete_message(message, reply_message)
    else:
        text = message.text.split()
        if len(text) > 1:
            user_id = message.from_user.id if text[1] == "me" else int(text[1])
        else:
            user_id = 0
            sid = message.chat.id
            if obj := Intervals["status"].get(sid):
                obj.cancel()
                del Intervals["status"][sid]
        await sendStatusMessage(message, user_id)
        await deleteMessage(message)


@new_task
async def status_pages(_, query):
    data = query.data.split()
    key = int(data[1])
    if data[2] == "ref":
        await query.answer()
        await update_status_message(key, force=True)
    elif data[2] in ["nex", "pre"]:
        await query.answer()
        async with task_dict_lock:
            if data[2] == "nex":
                status_dict[key]["page_no"] += status_dict[key]["page_step"]
            else:
                status_dict[key]["page_no"] -= status_dict[key]["page_step"]
    elif data[2] == "ps":
        await query.answer()
        async with task_dict_lock:
            status_dict[key]["page_step"] = int(data[3])
    elif data[2] == "st":
        await query.answer()
        async with task_dict_lock:
            status_dict[key]["status"] = data[3]
        await update_status_message(key, force=True)
    elif data[2] == "ov":
        tasks = {
            "Download": 0,
            "Upload": 0,
            "Seed": 0,
            "Archive": 0,
            "Extract": 0,
            "Split": 0,
            "QueueDl": 0,
            "QueueUp": 0,
            "Clone": 0,
            "CheckUp": 0,
            "Pause": 0,
            "SamVid": 0,
            "ConvertMedia": 0,
        }
        dl_speed = 0
        up_speed = 0
        seed_speed = 0
        async with task_dict_lock:
            for download in task_dict.values():
                match await sync_to_async(download.status):
                    case MirrorStatus.STATUS_DOWNLOADING:
                        tasks["Download"] += 1
                        dl_speed += speed_string_to_bytes(download.speed())
                    case MirrorStatus.STATUS_UPLOADING:
                        tasks["Upload"] += 1
                        up_speed += speed_string_to_bytes(download.speed())
                    case MirrorStatus.STATUS_SEEDING:
                        tasks["Seed"] += 1
                        seed_speed += speed_string_to_bytes(download.seed_speed())
                    case MirrorStatus.STATUS_ARCHIVING:
                        tasks["Archive"] += 1
                    case MirrorStatus.STATUS_EXTRACTING:
                        tasks["Extract"] += 1
                    case MirrorStatus.STATUS_SPLITTING:
                        tasks["Split"] += 1
                    case MirrorStatus.STATUS_QUEUEDL:
                        tasks["QueueDl"] += 1
                    case MirrorStatus.STATUS_QUEUEUP:
                        tasks["QueueUp"] += 1
                    case MirrorStatus.STATUS_CLONING:
                        tasks["Clone"] += 1
                    case MirrorStatus.STATUS_CHECKING:
                        tasks["CheckUp"] += 1
                    case MirrorStatus.STATUS_PAUSED:
                        tasks["Pause"] += 1
                    case MirrorStatus.STATUS_SAMVID:
                        tasks["SamVid"] += 1
                    case MirrorStatus.STATUS_CONVERTING:
                        tasks["ConvertMedia"] += 1
                    case _:
                        tasks["Download"] += 1
                        dl_speed += speed_string_to_bytes(download.speed())

        msg = f"""DL : {tasks['Download']} | UP : {tasks['Upload']} | SD : {tasks['Seed']} | AR : {tasks['Archive']}
EX : {tasks['Extract']} | SP : {tasks['Split']} | QD : {tasks['QueueDl']} | QU : {tasks['QueueUp']}
CL : {tasks['Clone']} | CH : {tasks['CheckUp']} | PA : {tasks['Pause']} | SV : {tasks['SamVid']}
CM : {tasks['ConvertMedia']}

📤𝑺𝒑𝒆𝒆𝒅 𝑼𝒏𝒅𝒖𝒉 : {get_readable_file_size(dl_speed)}/s
📥𝑺𝒑𝒆𝒆𝒅 𝑼𝒏𝒈𝒈𝒂𝒉 : {get_readable_file_size(up_speed)}/s

By: 🅿🅴🅰 🅼🅰🆂🅰🅼🅱🅰
"""
        await query.answer(msg, show_alert=True)


bot.add_handler(
    MessageHandler(
        mirror_status,
        filters=command(
            BotCommands.StatusCommand
        ) & CustomFilters.authorized,
    )
)
bot.add_handler(
    CallbackQueryHandler(
        status_pages, 
        filters=regex(
            "^status"
        )
    )
)
