#!/usr/bin/env python3
from re import match as re_match
from time import time
from html import escape
from psutil import virtual_memory, cpu_percent, disk_usage, net_io_counters
from asyncio import create_subprocess_exec, create_subprocess_shell, run_coroutine_threadsafe, sleep
from asyncio.subprocess import PIPE
from functools import partial, wraps
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession

from bot import download_dict, download_dict_lock, botStartTime, user_data, config_dict, bot_loop
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.ext_utils.telegraph_helper import telegraph

THREADPOOL = ThreadPoolExecutor(max_workers=1000)

MAGNET_REGEX = r'magnet:\?xt=urn:(btih|btmh):[a-zA-Z0-9]*\s*'

URL_REGEX = r'^(?!\/)(rtmps?:\/\/|mms:\/\/|rtsp:\/\/|https?:\/\/|ftp:\/\/)?([^\/:]+:[^\/@]+@)?(www\.)?(?=[^\/:\s]+\.[^\/:\s]+)([^\/:\s]+\.[^\/:\s]+)(:\d+)?(\/[^#\s]*[\s\S]*)?(\?[^#\s]*)?(#.*)?$'

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

STATUS_START = 0
PAGES = 1
PAGE_NO = 1


class MirrorStatus:
    STATUS_UPLOADING = "Unggah..."
    STATUS_DOWNLOADING = "Unduh..."
    STATUS_CLONING = "Kloning..."
    STATUS_QUEUEDL = "Nunggu Antri Unduh..."
    STATUS_QUEUEUP = "Nunggu Antri Unggah..."
    STATUS_PAUSED = "Dihentikan."
    STATUS_ARCHIVING = "Arsip..."
    STATUS_EXTRACTING = "Ekstrak..."
    STATUS_SPLITTING = "Membagi..."
    STATUS_CHECKING = "Ngecek..."
    STATUS_SEEDING = "Ngeseed..."


class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.task = bot_loop.create_task(self.__set_interval())

    async def __set_interval(self):
        while True:
            await sleep(self.interval)
            await self.action()

    def cancel(self):
        self.task.cancel()


def get_readable_file_size(size_in_bytes):
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024 and index < len(SIZE_UNITS) - 1:
        size_in_bytes /= 1024
        index += 1
    return f'{size_in_bytes:.2f}{SIZE_UNITS[index]}' if index > 0 else f'{size_in_bytes}B'


async def getDownloadByGid(gid):
    async with download_dict_lock:
        return next((dl for dl in download_dict.values() if dl.gid() == gid), None)


async def getAllDownload(req_status):
    async with download_dict_lock:
        if req_status == 'all':
            return list(download_dict.values())
        return [dl for dl in download_dict.values() if dl.status() == req_status]


def bt_selection_buttons(id_):
    gid = id_[:12] if len(id_) > 20 else id_
    pincode = ''.join([n for n in id_ if n.isdigit()][:4])
    buttons = ButtonMaker()
    BASE_URL = config_dict['BASE_URL']
    if config_dict['WEB_PINCODE']:
        buttons.ubutton("Select Files", f"{BASE_URL}/app/files/{id_}")
        buttons.ibutton("Pincode", f"btsel pin {gid} {pincode}")
    else:
        buttons.ubutton(
            "Select Files", f"{BASE_URL}/app/files/{id_}?pin_code={pincode}")
    buttons.ibutton("Done Selecting", f"btsel done {gid} {id_}")
    return buttons.build_menu(2)


async def get_telegraph_list(telegraph_content):
    path = [(await telegraph.create_page(title='Drive Pea Masamba', content=content))["path"] for content in telegraph_content]
    if len(path) > 1:
        await telegraph.edit_telegraph(path, telegraph_content)
    buttons = ButtonMaker()
    buttons.ubutton("🔦 VIEW", f"https://telegra.ph/{path[0]}")
    return buttons.build_menu(1)


def get_progress_bar_string(pct):
    pct = float(pct.strip('%'))
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = '■' * cFull
    p_str += '□' * (12 - cFull)
    return f"[{p_str}]"


def get_readable_message():
    msg = "<b><a href='https://subscene.com/u/1271292'>🄿🅴🄰 🅼🄰🅂🄰🅼🄱🄰</a> </b>\n\n"
    button = None
    STATUS_LIMIT = config_dict['STATUS_LIMIT']
    tasks = len(download_dict)
    globals()['PAGES'] = (tasks + STATUS_LIMIT - 1) // STATUS_LIMIT
    if PAGE_NO > PAGES and PAGES != 0:
        globals()['STATUS_START'] = STATUS_LIMIT * (PAGES - 1)
        globals()['PAGE_NO'] = PAGES
    for download in list(download_dict.values())[STATUS_START:STATUS_LIMIT+STATUS_START]:
        msg += f"<code>{escape(f'{download.name()}')}</code>"
        if download.status() not in [MirrorStatus.STATUS_SPLITTING, MirrorStatus.STATUS_SEEDING]:
            msg += f"\n<b>┌┤{get_progress_bar_string(download.progress())} <code>{download.progress()}</code>├┐</b>"
            if download.message.chat.type.name in ['SUPERGROUP', 'CHANNEL']:
                msg += f"\n<b>├ Status :</b> <a href='{download.message.link}'>{download.status()}</a>"
            else:
                msg += f"\n<b>├ Status :</b> <code>{download.status()}</code>"
            msg += f"\n<b>├ Proses :</b> <code>{download.processed_bytes()}</code> dari <code>{download.size()}</code>"
            msg += f"\n<b>├ Kec :</b> <code>{download.speed()}</code> | <b>ETA :</b> <code>{download.eta()}</code>"
            if hasattr(download, 'seeders_num'):
                try:
                    msg += f"\n<b>├ Seeders :</b> <code>{download.seeders_num()}</code> | <b>Leechers :</b> <code>{download.leechers_num()}</code>"
                except:
                    pass
        elif download.status() == MirrorStatus.STATUS_SEEDING:
            if download.message.chat.type.name in ['SUPERGROUP', 'CHANNEL']:
                msg += f"\n<b>┌ Status :</b> <a href='{download.message.link}'>{download.status()}</a>"
            else:
                msg += f"\n<b>┌ Status :</b> <code>{download.status()}</code>"
            msg += f"\n<b>├ Ukuran :</b> <code>{download.size()}</code>"
            msg += f"\n<b>├ Kec :</b> <code>{download.upload_speed()}</code> | <b>Diupload :</b> <code>{download.uploaded_bytes()}</code>"
            msg += f"\n<b>├ Ratio :</b> <code>{download.ratio()}</code> | <b>Waktu :</b> <code>{download.seeding_time()}</code>"
        else:
            if download.message.chat.type.name in ['SUPERGROUP', 'CHANNEL']:
                msg += f"\n<b>┌ Status :</b> <a href='{download.message.link}'>{download.status()}</a>"
            else:
                msg += f"\n<b>┌ Status :</b> <code>{download.status()}</code>"
            msg += f"\n<b>├ Ukuran :</b> <code>{download.size()}</code>"
        # <a href='tg://user?id={download.message.from_user.id}'>{download.message.from_user.first_name}</a>
        msg += f"\n<b>├ User :</b> <code>{download.message.from_user.first_name}</code> | <b>ID :</b> <code>{download.message.from_user.id}</code>"
        msg += f"\n<b>└</b> <code>/{BotCommands.CancelMirror[0]} {download.gid()}</code>\n\n"
    if len(msg) == 0:
        return None, None
    dl_speed = 0
    up_speed = 0
    for download in download_dict.values():
        tstatus = download.status()
        if tstatus == MirrorStatus.STATUS_DOWNLOADING:
            spd = download.speed()
            if 'K' in spd:
                dl_speed += float(spd.split('K')[0]) * 1024
            elif 'M' in spd:
                dl_speed += float(spd.split('M')[0]) * 1048576
        elif tstatus == MirrorStatus.STATUS_UPLOADING:
            spd = download.speed()
            if 'K' in spd:
                up_speed += float(spd.split('K')[0]) * 1024
            elif 'M' in spd:
                up_speed += float(spd.split('M')[0]) * 1048576
        elif tstatus == MirrorStatus.STATUS_SEEDING:
            spd = download.upload_speed()
            if 'K' in spd:
                up_speed += float(spd.split('K')[0]) * 1024
            elif 'M' in spd:
                up_speed += float(spd.split('M')[0]) * 1048576
    if tasks > STATUS_LIMIT:
        msg += f"<b>Halaman :</b> <code>{PAGE_NO}/{PAGES}</code> | <b>Total Tugas :</b> <code>{tasks}</code>\n"
        buttons = ButtonMaker()
        buttons.ibutton("⫷", "status pre")
        buttons.ibutton("🪫", "status ref")
        buttons.ibutton("⫸", "status nex")
        button = buttons.build_menu(3)   
    msg += "________< 𝙲 𝙼 𝚃 >___________"
    msg += f"\n<b>🅲🄿🆄 :</b> <code>{cpu_percent()}%</code> | <b>🆁🄰🅼 :</b> <code>{virtual_memory().percent}%</code>"    
    msg += f"\n<b>🆃🄳🅻 :</b> <code>{get_readable_file_size(net_io_counters().bytes_recv)}</code> | <b>🆃🅄🅻 :</b> <code>{get_readable_file_size(net_io_counters().bytes_sent)}</code>"
    msg += f"\n<b>🄳🅸🆂🄺 :</b> <code>{get_readable_file_size(disk_usage(config_dict['DOWNLOAD_DIR']).free)}</code> | <b>🅃🅸🅼🄴 :</b> <code>{get_readable_time(time() - botStartTime)}</code>"
    msg += f"\n<b>▼ :</b> <code>{get_readable_file_size(dl_speed)}/s</code> | <b>▲ :</b> <code>{get_readable_file_size(up_speed)}/s</code>"
    return msg, button


async def turn_page(data):
    STATUS_LIMIT = config_dict['STATUS_LIMIT']
    global STATUS_START, PAGE_NO
    async with download_dict_lock:
        if data[1] == "nex":
            if PAGE_NO == PAGES:
                STATUS_START = 0
                PAGE_NO = 1
            else:
                STATUS_START += STATUS_LIMIT
                PAGE_NO += 1
        elif data[1] == "pre":
            if PAGE_NO == 1:
                STATUS_START = STATUS_LIMIT * (PAGES - 1)
                PAGE_NO = PAGES
            else:
                STATUS_START -= STATUS_LIMIT
                PAGE_NO -= 1


def get_readable_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result


def is_magnet(url):
    magnet = re_match(MAGNET_REGEX, url)
    return bool(magnet)


def is_url(url):
    url = re_match(URL_REGEX, url)
    return bool(url)


def is_gdrive_link(url):
    return "drive.google.com" in url


def is_telegram_link(url):
    return url.startswith(('https://t.me/', 'tg://openmessage?user_id='))


def is_share_link(url):
    return bool(re_match(r'https?:\/\/.+\.gdtot\.\S+|https?:\/\/(filepress|filebee|appdrive|gdflix|sharer)\.\S+', url))


def is_mega_link(url):
    return "mega.nz" in url or "mega.co.nz" in url


def is_rclone_path(path):
    return bool(re_match(r'^(mrcc:)?(?!magnet:)(?!mtp:)(?![- ])[a-zA-Z0-9_\. -]+(?<! ):(?!.*\/\/).*$|^rcl$', path))


def is_gdrive_id(id_):
    return bool(re_match(r'^(mtp:)?(?:[a-zA-Z0-9-_]{33}|[a-zA-Z0-9_-]{19})$|^gdl$|^root$', id_))


def get_mega_link_type(url):
    return "folder" if "folder" in url or "/#F!" in url else "file"


def arg_parser(items, arg_base):
    if not items:
        return arg_base
    bool_arg_set = {'-b', '-e', '-z', '-s', '-j', '-d'}
    t = len(items)
    i = 0
    arg_start = -1

    while i + 1 <= t:
        part = items[i].strip()
        if part in arg_base:
            if arg_start == -1:
                arg_start = i
            if i + 1 == t and part in bool_arg_set or part in ['-s', '-j']:
                arg_base[part] = True
            else:
                sub_list = []
                for j in range(i + 1, t):
                    item = items[j].strip()
                    if item in arg_base:
                        if part in bool_arg_set and not sub_list:
                            arg_base[part] = True
                        break
                    sub_list.append(item.strip())
                    i += 1
                if sub_list:
                    arg_base[part] = " ".join(sub_list)
        i += 1

    link = []
    if items[0].strip() not in arg_base:
        if arg_start == -1:
            link.extend(item.strip() for item in items)
        else:
            link.extend(items[r].strip() for r in range(arg_start))
        if link:
            arg_base['link'] = " ".join(link)
    return arg_base


async def get_content_type(url):
    try:
        async with ClientSession(trust_env=True) as session:
            async with session.get(url, verify_ssl=False) as response:
                return response.headers.get('Content-Type')
    except:
        return None
        

def update_user_ldata(id_, key, value):
    user_data.setdefault(id_, {})
    user_data[id_][key] = value


async def cmd_exec(cmd, shell=False):
    if shell:
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    return stdout, stderr, proc.returncode


def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return bot_loop.create_task(func(*args, **kwargs))
    return wrapper


async def sync_to_async(func, *args, wait=True, **kwargs):
    pfunc = partial(func, *args, **kwargs)
    future = bot_loop.run_in_executor(THREADPOOL, pfunc)
    return await future if wait else future


def async_to_sync(func, *args, wait=True, **kwargs):
    future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
    return future.result() if wait else future


def new_thread(func):
    @wraps(func)
    def wrapper(*args, wait=False, **kwargs):
        future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
        return future.result() if wait else future
    return wrapper
