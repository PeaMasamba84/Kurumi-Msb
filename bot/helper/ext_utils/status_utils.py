from asyncio import iscoroutinefunction
from html import escape
from psutil import (
    cpu_percent, 
    disk_usage, 
    net_io_counters,
    virtual_memory
)
from time import time

from bot import (
    DOWNLOAD_DIR,
    task_dict,
    task_dict_lock,
    botStartTime,
    config_dict,
    status_dict,
)
from bot.helper.ext_utils.bot_utils import sync_to_async
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker


SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]

class MirrorStatus:
    STATUS_DOWNLOADING = "Unduh"
    STATUS_UPLOADING = "Unggah"
    STATUS_CLONING = "Clone"
    STATUS_QUEUEDL = "AntriDownload"
    STATUS_QUEUEUP = "AntriUpload"
    STATUS_PAUSED = "Henti"
    STATUS_CHECKING = "Cek"
    STATUS_ARCHIVING = "Arsip"
    STATUS_EXTRACTING = "Ekstrak"
    STATUS_SEEDING = "Seed"
    STATUS_SPLITTING = "Bagi"
    STATUS_SAMVID = "SampelVideo"
    STATUS_CONVERTING = "Konversi"
     
STATUSES = {
    "ALL": "All",
    "DL": MirrorStatus.STATUS_DOWNLOADING,
    "UP": MirrorStatus.STATUS_UPLOADING,
    "CL": MirrorStatus.STATUS_CLONING,
    "QD": MirrorStatus.STATUS_QUEUEDL,
    "QU": MirrorStatus.STATUS_QUEUEUP,
    "PA": MirrorStatus.STATUS_PAUSED,
    "CK": MirrorStatus.STATUS_CHECKING,
    "AR": MirrorStatus.STATUS_ARCHIVING,
    "EX": MirrorStatus.STATUS_EXTRACTING,
    "SD": MirrorStatus.STATUS_SEEDING,
    "SP": MirrorStatus.STATUS_SPLITTING,
    "SV": MirrorStatus.STATUS_SAMVID,
    "CM": MirrorStatus.STATUS_CONVERTING,
}


async def getTaskByGid(gid: str):
    async with task_dict_lock:
        for tk in list(task_dict.values()):
            if hasattr(tk, "seeding"):
                await sync_to_async(tk.update)
            if tk.gid() == gid:
                return tk
        return None


def getSpecificTasks(status, userId):
    if status == "All":
        if userId:
            return [
                tk for tk in list(task_dict.values()) if tk.listener.userId == userId
            ]
        else:
            return list(task_dict.values())
    elif userId:
        return [
            tk
            for tk in list(task_dict.values())
            if tk.listener.userId == userId
            and (
                (st := tk.status() == status)
                or status == MirrorStatus.STATUS_DOWNLOADING
                and st not in list(STATUSES.values())
            )
        ]
    else:
        return [
            tk
            for tk in list(task_dict.values())
            if (st := tk.status() == status)
            or status == MirrorStatus.STATUS_DOWNLOADING
            and st not in list(STATUSES.values())
        ]



async def getAllTasks(req_status: str, userId):
    async with task_dict_lock:
        return await sync_to_async(getSpecificTasks, req_status, userId)


def get_readable_file_size(size_in_bytes: int):
    if size_in_bytes is None:
        return "0B"
    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1
    return (
        f"{size_in_bytes:.2f}{SIZE_UNITS[index]}"
        if index > 0
        else f"{size_in_bytes:.2f}B"
    )

def get_readable_time(seconds: int):
    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    result = ""
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    return result


def speed_string_to_bytes(size_text: str):
    size = 0
    size_text = size_text.lower()
    if "k" in size_text:
        size += float(size_text.split("k")[0]) * 1024
    elif "m" in size_text:
        size += float(size_text.split("m")[0]) * 1048576
    elif "g" in size_text:
        size += float(size_text.split("g")[0]) * 1073741824
    elif "t" in size_text:
        size += float(size_text.split("t")[0]) * 1099511627776
    elif "b" in size_text:
        size += float(size_text.split("b")[0])
    return size


def get_progress_bar_string(pct) -> str:
    if not isinstance(pct, float):
        pct = float(pct.strip("%"))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = "■" * cFull
    p_str += "□" * (12 - cFull)
    return f"[{p_str}]"


async def get_readable_message(sid, is_user, page_no=1, status="All", page_step=1):
    msg = "<a href='https://subscene.com/u/1271292'>𝐒𝐔𝐁𝐓𝐈𝐓𝐋𝐄 𝐏𝐄𝐀 𝐌𝐀𝐒𝐀𝐌𝐁𝐀</a>\n"
    button = None

    tasks = await sync_to_async(getSpecificTasks, status, sid if is_user else None)

    STATUS_LIMIT = config_dict["STATUS_LIMIT"]
    tasks_no = len(tasks)
    pages = (max(tasks_no, 1) + STATUS_LIMIT - 1) // STATUS_LIMIT
    if page_no > pages:
        page_no = (page_no - 1) % pages + 1
        status_dict[sid]["page_no"] = page_no
    elif page_no < 1:
        page_no = pages - (abs(page_no) % pages)
        status_dict[sid]["page_no"] = page_no
    start_position = (page_no - 1) * STATUS_LIMIT

    for _, task in enumerate(
        tasks[start_position : STATUS_LIMIT + start_position], start=1
    ):
        tstatus = await sync_to_async(task.status) if status == "All" else status
        if task.listener.isPrivateChat:             
            msg += f"\n💾 File :<blockquote><code>>RAHASIA YA</code></blockquote>"
        else: 
            msg += f"\n💾 File :<blockquote><code>{escape(f'{task.name()}')}</code></blockquote>\n"
        progress = (
            await task.progress()
            if iscoroutinefunction(task.progress)
            else task.progress()
        )
        msg += f"\n<b>┌┤{get_progress_bar_string(progress)} <code>»{progress}</code></b>"
        if task.listener.isSuperChat:
            msg += f"\n<b>├📲 Status:</b> <a href='{task.listener.message.link}'>{tstatus}</a>"
        else:
            msg += f"\n<b>├📲 Status:</b> <code>{tstatus}</code>"
        if tstatus not in [
            MirrorStatus.STATUS_SPLITTING,
            MirrorStatus.STATUS_SEEDING,
            MirrorStatus.STATUS_SAMVID,
            MirrorStatus.STATUS_CONVERTING,
            MirrorStatus.STATUS_QUEUEUP,
        ]:
            msg += f"\n<b>├🔄 Proses:</b> <code>{task.processed_bytes()}</code> of <code>{task.size()}</code>"
            msg += f"\n<b>├🕰 Estimasi:</b> <code>{task.eta()}</code>"
            msg += f"\n<b>├🛜 Kecepatan:</b> <code>{task.speed()}</code>"
            if hasattr(task, "seeders_num"):
                try:
                    msg += f"\n<b>├🌱 Seeders :</b> <code>{task.seeders_num()}</code>"
                    msg += f"\n<b>├🐌 Leechers :</b> <code>{task.leechers_num()}</code>"
                except:
                    pass
        elif tstatus == MirrorStatus.STATUS_SEEDING:
            msg += f"\n<b>├🚦 Rasio: </b> <code>{task.ratio()}</code>"
            msg += f"\n<b>├⏰ Waktu: </b> <code>{task.seeding_time()}</code>"
            msg += f"\n<b>├📦 Ukuran: </b> <code>{task.size()}</code>"
            msg += f"\n<b>├◭ Diupload: </b> <code>{task.uploaded_bytes()}</code>"
            msg += f"\n<b>├🛸 Kecepatan: </b> <code>{task.seed_speed()}</code>"
        else:
            msg += f"\n<b>├📦 Ukuran : </b> <code>{task.size()}</code>"
            
        tgid = task.gid()
        msg += f"\n<b>├📟 GID:</b> <code>{tgid}</code>"
        
        if task.listener.isPrivateChat: 
            msg += f"\n<b>├🆔 UID:</b> <code>PRIVATE</code>"
            msg += f"\n<b>├🦹 User:</b> <code>PRIVATE</code>"
        else:
            msg += f"\n<b>├🆔 UID:</b> <code>{task.listener.userId}</code>"
            msg += f"\n<b>├🦹 User:</b> <code>{task.listener.user.first_name} {(task.listener.user.last_name or '')}</code>"
            
        msg += f"\n<b>├📵 Stop:</b> <code>/{BotCommands.CancelTaskCommand[1]} {tgid}</code>"
        msg += f"\n└┤<code>/{BotCommands.ForceStartCommand[1]} {tgid}</code>\n\n"

    if len(msg) == 0:
        if status == "All":
            return None, None
        else:
            msg = f"<b>Tidak ada Tugas</b> <code>{status}</code>!\n\n"
    buttons = ButtonMaker()
    if not is_user:
        buttons.ibutton("Stats", f"status {sid} ov", position="header")
    if len(tasks) > STATUS_LIMIT:
        # msg += f"<b>Step :</b> <code>{page_step}</code>"
        msg += f"<b>Halaman :</b> <code>{page_no}/{pages}</code>"
        msg += f"\n<b>Total Tugas :</b> <code>{tasks_no}</code>\n\n"
        buttons.ibutton("⫷", f"status {sid} pre", position="header")
        buttons.ibutton("⫸", f"status {sid} nex", position="header")
        if tasks_no > 30:
            for i in [1, 2, 4, 6, 8, 10, 15]:
                buttons.ibutton(i, f"status {sid} ps {i}", position="footer")
    if status != "All" or tasks_no > 20:
        for label, status_value in list(STATUSES.items())[:9]:
            if status_value != status:
                buttons.ibutton(label, f"status {sid} st {status_value}")
    buttons.ibutton("Refresh", f"status {sid} ref", position="header")
    button = buttons.build_menu(8)
    msg += "<a href='https://t.me/+Tka9XvaTDe8zZjY1'>═══❰ 𝙿𝚎𝚊 𝙼𝚊𝚜𝚊𝚖𝚋𝚊 ❱═══</a>"
    msg += f"\n<b>💿CPU:</b> <code>{cpu_percent()}%</code> | <b>🚦RAM:</b> <code>{virtual_memory().percent}%</code>"
    msg += f"\n<b>▼:</b> <code>{get_readable_file_size(net_io_counters().bytes_recv)}</code> | <b>▲:</b> <code>{get_readable_file_size(net_io_counters().bytes_sent)}</code>"
    return msg, button
