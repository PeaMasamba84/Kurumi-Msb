from time import time
from html import escape
from psutil import (
    cpu_percent, 
    disk_usage, 
    net_io_counters,
    virtual_memory
)

from bot import task_dict, task_dict_lock, botStartTime, config_dict
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker


SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]

class MirrorStatus:
    STATUS_DOWNLOADING = "📤𝑼𝒏𝒅𝒖𝒉"
    STATUS_UPLOADING = "📥𝑼𝒏𝒈𝒈𝒂𝒉"
    STATUS_QUEUEDL = "⌚️𝑨𝒏𝒕𝒓𝒊𝑫𝒐𝒘𝒏"
    STATUS_QUEUEUP = "⌚️𝑨𝒏𝒕𝒓𝒊𝑼𝒑"
    STATUS_PAUSED = "💤𝑱𝒆𝒅𝒂"
    STATUS_ARCHIVING = "📚𝑨𝒓𝒔𝒊𝒑"
    STATUS_EXTRACTING = "🔄𝑬𝒌𝒔𝒕𝒓𝒂𝒌"
    STATUS_CLONING = "🧬𝑪𝒍𝒐𝒏𝒆"
    STATUS_SEEDING = "🌱𝑺𝒆𝒆𝒅"
    STATUS_SPLITTING = "✂𝑴𝒆𝒎𝒃𝒂𝒈𝒊"
    STATUS_CHECKING = "📝𝑪𝒆𝒌"
    STATUS_SAMVID = "🎞𝑺𝒂𝒎𝒑𝒍𝒆𝑽𝒊𝒅𝒆𝒐"
     
STATUS_VALUES = [
    ("𝐀𝐋𝐋", "All"),
    ("𝐃𝐋", MirrorStatus.STATUS_DOWNLOADING),
    ("𝐔𝐏", MirrorStatus.STATUS_UPLOADING),
    ("𝐐𝐃", MirrorStatus.STATUS_QUEUEDL),
    ("𝐐𝐔", MirrorStatus.STATUS_QUEUEUP),
    ("𝐀𝐑", MirrorStatus.STATUS_ARCHIVING),
    ("𝐄𝐗", MirrorStatus.STATUS_EXTRACTING),
    ("𝐂𝐋", MirrorStatus.STATUS_CLONING),
    ("𝐒𝐃", MirrorStatus.STATUS_SEEDING),
    ("𝐒𝐕", MirrorStatus.STATUS_SAMVID)
]


async def getTaskByGid(gid: str):
    async with task_dict_lock:
        return next((tk for tk in task_dict.values() if tk.gid() == gid), None)


async def getAllTasks(req_status: str):
    async with task_dict_lock:
        if req_status == "all":
            return list(task_dict.values())
        return [tk for tk in task_dict.values() if tk.status() == req_status]


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


def get_progress_bar_string(pct):
    pct = float(pct.strip("%"))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = "■" * cFull
    p_str += "□" * (12 - cFull)
    return f"[{p_str}]"


def get_readable_message(sid, is_user, page_no=1, status="All", page_step=1):
    msg = ""
    button = None

    if status == "All":
        tasks = (
            [tk for tk in task_dict.values() if tk.listener.user_id == sid]
            if is_user
            else list(task_dict.values())
        )
    elif is_user:
        tasks = [
            tk
            for tk in task_dict.values()
            if tk.status() == status and tk.listener.user_id == sid
        ]
    else:
        tasks = [tk for tk in task_dict.values() if tk.status() == status]

    STATUS_LIMIT = config_dict["STATUS_LIMIT"]
    tasks_no = len(tasks)
    pages = (max(tasks_no, 1) + STATUS_LIMIT - 1) // STATUS_LIMIT
    if page_no > pages:
        page_no = (page_no - 1) % pages + 1
    elif page_no < 1:
        page_no = pages - (abs(page_no) % pages)
    start_position = (page_no - 1) * STATUS_LIMIT

    for index, task in enumerate(
        tasks[start_position : STATUS_LIMIT + start_position], start=1
    ):
        tstatus = task.status()
        if task.listener.isPrivateChat: 
            msg += f"\n💾 File :<blockquote><code>PRIVATE</code></blockquote>"
        else: 
            msg += f"\n💾 File :<blockquote><code>{escape(f'{task.name()}')}</code></blockquote>\n"
        msg += f"\n<b>┌┤{get_progress_bar_string(task.progress())} <code>{task.progress()}</code>├┐</b>"
        if task.listener.isSuperChat:
            msg += f"\n<b>┌📲 Status :</b> <a href='{task.listener.message.link}'>{tstatus}</a>"
        else:
            msg += f"\n<b>┌📲 Status :</b> <code>{tstatus}</code>"
        if tstatus not in [
            MirrorStatus.STATUS_SPLITTING,
            MirrorStatus.STATUS_SEEDING,
            MirrorStatus.STATUS_SAMVID,
        ]:
            msg += f"\n<b>├🔄 Proses :</b> <code>{task.processed_bytes()}</code> dari <code>{task.size()}</code>"
            msg += f"\n<b>├🕰 Estimasi :</b> <code>{task.eta()}</code>"
            msg += f"\n<b>├🛸 Kecepatan :</b> <code>{task.speed()}</code>"
            if hasattr(task, "seeders_num"):
                try:
                    msg += f"\n<b>├🌱 Seed :</b> <code>{task.seeders_num()}</code>"
                    msg += f"\n<b>├🐌 Leech :</b> <code>{task.leechers_num()}</code>"
                except:
                    pass
        elif tstatus == MirrorStatus.STATUS_SEEDING:
            msg += f"\n<b>├🚦 Rasio : </b> <code>{task.ratio()}</code>"
            msg += f"\n<b>├⏰ Waktu : </b> <code>{task.seeding_time()}</code>"
            msg += f"\n<b>├📦 Ukuran : </b> <code>{task.size()}</code>"
            msg += f"\n<b>├◭ Diupload : </b> <code>{task.uploaded_bytes()}</code>"
            msg += f"\n<b>├🛸 Kecepatan : </b> <code>{task.seed_speed()}</code>"
        else:
            msg += f"\n<b>├📦 Ukuran : </b> <code>{task.size()}</code>"
        if task.listener.isPrivateChat: 
            msg += f"\n<b>├🔖 ID :</b> <code>PRIVATE</code>"
            msg += f"\n<b>├🦹 User :</b> <code>PRIVATE</code>" 
        else:
            msg += f"\n<b>├🔖 ID :</b> <code>{task.listener.message.from_user.id}</code>"
            msg += f"\n<b>├🦹 User :</b> <code>{task.listener.message.from_user.first_name}</code>"
        msg += f"\n<b>└📵 Stop :</b> <code>/{BotCommands.CancelTaskCommand[0]} {task.gid()}</code>\n\n"

    if len(msg) == 0 and status == "All":
        return None, None
    elif len(msg) == 0:
        msg = f"<b>Tidak ada tugas</b> <code>{status}</code>!\n\n"
    buttons = ButtonMaker()
    if not is_user:
        buttons.ibutton("S̲t̲a̲t̲s̲​​​​​", "status 0 ov", position="header")
    if len(tasks) > STATUS_LIMIT:
        msg += f"<b>Hal:</b> {page_no}/{pages} | <b>Tugas:</b> {tasks_no} | <b>Step:</b> {page_step}\n"        
        buttons.ibutton("⫷", f"status {sid} pre", position="header")
        buttons.ibutton("⫸", f"status {sid} nex", position="header")
        if tasks_no > 30:
            for i in [1, 2, 4, 6, 8, 10, 15, 20]:
                buttons.ibutton(i, f"status {sid} ps {i}", position="footer")
    if status != "All" or tasks_no > 20:
        for label, status_value in STATUS_VALUES:
            if status_value != status:
                buttons.ibutton(label, f"status {sid} st {status_value}")
    buttons.ibutton("📵", f"status {sid} ref", position="header")
    button = buttons.build_menu(8)
    msg += "═══❰ 𝑃𝑒𝑎 𝑀𝑎𝑠𝑎𝑚𝑏𝑎 ❱═══"
    msg += f"\n<b>▼:</b> <code>{get_readable_file_size(net_io_counters().bytes_recv)}</code> | <b>▲:</b> <code>{get_readable_file_size(net_io_counters().bytes_sent)}</code> | <b>🕯:</b> <code>{get_readable_time(time() - botStartTime)}</code>"
    return msg, button
