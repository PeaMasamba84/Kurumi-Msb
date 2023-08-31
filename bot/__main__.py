#!/usr/bin/env python3
from signal import signal, SIGINT
from aiofiles.os import path as aiopath, remove as aioremove
from aiofiles import open as aiopen
from os import execl as osexecl
from psutil import disk_usage, cpu_percent, cpu_count, virtual_memory, net_io_counters, boot_time, cpu_freq
from time import time
from sys import executable
from pyrogram import __version__ as prv
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from asyncio import create_subprocess_exec, gather
from subprocess import check_output
from quoters import Quote
from pytz import timezone
from datetime import datetime

from bot import bot, botStartTime, LOGGER, Interval, DATABASE_URL, QbInterval, INCOMPLETE_TASK_NOTIFIER, scheduler, config_dict, arv, ffv, gav, msv, p7v, prv, rcv, qbv, ytv
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time, cmd_exec, sync_to_async
from .helper.ext_utils.db_handler import DbManger
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, editMessage, sendFile
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from bot.helper.listeners.aria2_listener import start_aria2_listener
from .modules import authorize, clone, gd_count, gd_delete, cancel_mirror, gd_search, mirror_leech, status, torrent_search, torrent_select, ytdlp, rss, shell, eval, users_settings, bot_settings, speedtest

def get_quotes():
    try:
        quotez = str(Quote.print_series_quote())
        quote = quotez.split(": ")[1]
        oleh = quotez.split(":")[0]
        quotes = f"{quote}\n~{oleh}"
    except:
        quotes = "Ngga ada Quote bijak buatmu wahai Tuan yang bijaksana :D"
    return quotes


def progress_bar(percentage):
    if isinstance(percentage, str):
        return 'NaN'
    try:
        percentage = int(percentage)
    except:
        percentage = 0
    return ''.join(
        '■' if i <= percentage // 10 else '□' for i in range(1, 11)
    )


async def stats(_, message):
    if await aiopath.exists('.git'):
        last_commit = await cmd_exec("git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'", True)
        last_commit = last_commit[0]
    else:
        last_commit = 'UPSTREAM_REPO tidak ditemukan!'
    currentTime = get_readable_time(time() - botStartTime)
    osUptime = get_readable_time(time() - boot_time())
    total, used, free, disk = disk_usage(config_dict['DOWNLOAD_DIR'])
    try:
        total = get_readable_file_size(total)
    except:
        total = 'n/a'
    try:
        used = get_readable_file_size(used)
    except:
        used = 'n/a'
    try:
        free = get_readable_file_size(free)
    except:
        free = 'n/a'
    # Net Usage
    try:
        sent = get_readable_file_size(net_io_counters().bytes_sent)
    except:
        sent = 'n/a'
    try:
        recv = get_readable_file_size(net_io_counters().bytes_recv)
    except:
        recv = 'n/a'
    # Cpu
    cpuUsage = cpu_percent(interval=0.5)
    try:
        p_core = cpu_count(logical=False)
    except:
        p_core = 'n/a'
    try:
        t_core = cpu_count(logical=True)
    except:
        t_core = 'n/a'
    try:
        cpufreq = cpu_freq()
    except:
        cpufreq = 'n/a'
    try:
        freqcurrent = round(cpufreq.current)
    except:
        freqcurrent = 'n/a'
    memory = virtual_memory()
    mem_p = memory.percent
    try:
        mem_t = get_readable_file_size(memory.total)
    except:
        mem_t = 'n/a'
    try:
        mem_a = get_readable_file_size(memory.available)
    except:
        mem_a = 'n/a'
    try:
        mem_u = get_readable_file_size(memory.used)
    except:
        mem_u = 'n/a'
    # Neofetch
    neofetch = check_output(
        ["neofetch --shell_version off --stdout"], shell=True).decode()
    # Versi
    stats = f'''
<pre languange="bash">
<code>{neofetch}</code>
<b>CPU</b>
<b>Cores        :</b> <code>{p_core}</code>
<b>Logical      :</b> <code>{t_core}</code>
<b>Frequency    :</b> <code>{freqcurrent}</code>
<code>[{progress_bar(cpuUsage)}] {cpuUsage}%</code>

<b>RAM</b> 
<b>Terpakai     :</b> <code>{mem_u}</code>
<b>Tersedia     :</b> <code>{mem_a}</code>
<b>Total        :</b> <code>{mem_t}</code>
<code>[{progress_bar(mem_p)}] {mem_p}%</code>

<b>Penyimpanan</b> 
<b>Terpakai     :</b> <code>{used}</code>
<b>Tersedia     :</b> <code>{free}</code>
<b>Total        :</b> <code>{total}</code>
<code>[{progress_bar(disk)}] {disk}%</code>

<b>Jaringan</b>
<b>Unduhan      :</b> <code>{recv}</code>
<b>Unggahan     :</b> <code>{sent}</code>

<b>Versi</b>
<b>Aria2c       :</b> <code>v{arv}</code>
<b>FFMPEG       :</b> <code>v{ffv}</code>
<b>Google Api   :</b> <code>v{gav}</code>
<b>MegaSDK      :</b> <code>v{msv}</code>
<b>P7Zip        :</b> <code>v{p7v}</code>
<b>Pyrogram     :</b> <code>v{prv}</code>
<b>Rclone       :</b> <code>{rcv}</code>
<b>Qbittorrent  :</b> <code>{qbv}</code>
<b>YT-DLP       :</b> <code>v{ytv}</code>

<b>Lainnya</b>
<b>Username     :</b> <code>@{bot.me.username}</code>
<b>Waktu Bot    :</b> <code>{currentTime}</code>
<b>Waktu Mesin  :</b> <code>{osUptime}</code>
<b>Diperbarui   :</b> <code>{last_commit}</code>

<b>Quotes       :</b> 
<code>{get_quotes()}</code>
</pre>
'''
    await sendMessage(message, stats)


async def start(client, message):
    buttons = ButtonMaker()
    buttons.ubutton(
        "Website", "https://www.comelmuewa84.eu.org/")
    buttons.ubutton("Group", "https://t.me/CollectionMovie_Subtitles")
    reply_markup = buttons.build_menu(2)
    if await CustomFilters.authorized(client, message):
        start_string = f'''
<b>Mirror Tautan Lambat menjadi Tautan Cepat!</b>

<b>Note :</b>
Selalu backup File setelah Mirror untuk menghindari Drive terhapus!

Ketik <code>/{BotCommands.HelpCommand[0]}</code> untuk mendapatkan list perintah yang tersedia!

Enjoy :D
'''
        await sendMessage(message, start_string, reply_markup)
    else:
        await sendMessage(message, 'Tidak ada izin!\nGabung grup untuk menggunakan Bot!', reply_markup)


async def restart(_, message):
    restart_message = await sendMessage(message, "Restarting...")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    for interval in [QbInterval, Interval]:
        if interval:
            interval[0].cancel()
    await sync_to_async(clean_all)
    proc1 = await create_subprocess_exec('pkill', '-9', '-f', 'gunicorn|chrome|firefox|opera|edge')
    proc2 = await create_subprocess_exec('python3', 'update.py')
    await gather(proc1.wait(), proc2.wait())
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    osexecl(executable, executable, "-m", "bot")


async def ping(_, message):
    start_time = int(round(time() * 1000))
    reply = await sendMessage(message, "Mengetest waktu respon bot...")
    end_time = int(round(time() * 1000))
    await editMessage(reply, f'🤖 <b>Respon Bot :</b> <code>{end_time - start_time} ms</code>')


async def log(_, message):
    await sendFile(message, 'log.txt')

help_string = f'''
/{BotCommands.MirrorCommand[0]} atau /{BotCommands.MirrorCommand[1]} : Mirror ke Google Drive / Cloud.
/{BotCommands.QbMirrorCommand[0]} atau /{BotCommands.QbMirrorCommand[1]} : Mirror ke Google Drive / Cloud menggunakan qBittorrent.
/{BotCommands.YtdlCommand[0]} atau /{BotCommands.YtdlCommand[1]} : Mirror link yang disupport YT-DLP.
/{BotCommands.LeechCommand[0]} atau /{BotCommands.LeechCommand[1]} : Leech ke Telegram.
/{BotCommands.QbLeechCommand[0]} atau /{BotCommands.QbLeechCommand[1]} : Leech ke Telegram menggunakan qBittorrent.
/{BotCommands.YtdlLeechCommand[0]} atau /{BotCommands.YtdlLeechCommand[1]} : Leech link yang disupport YT-DLP.
/{BotCommands.CloneCommand[0]} atau /{BotCommands.CloneCommand[1]} [drive_url] : Menggandakan file/folder Google Drive.
/{BotCommands.CountCommand[0]} atau /{BotCommands.CountCommand[1]} [drive_url] : Menghitung file/folder Google Drive.
/{BotCommands.DeleteCommand[0]} atau /{BotCommands.DeleteCommand[1]} [drive_url] : Menghapus file/folder Google Drive (Hanya Owner & Sudo).
/{BotCommands.UserSetCommand[0]} atau /{BotCommands.UserSetCommand[1]} : Pengaturan User.
/{BotCommands.BotSetCommand[0]} atau /{BotCommands.BotSetCommand[1]} : Pengaturan Bot (Hanya Owner & Sudo).
/{BotCommands.BtSelectCommand[0]} atau /{BotCommands.BtSelectCommand[1]} : Memilih file dari torrent.
/{BotCommands.CancelMirror[0]} atau /{BotCommands.CancelMirror[1]} : Membatalkan tugas.
/{BotCommands.CancelAllCommand[0]} atau /{BotCommands.CancelAllCommand[1]} : Membatalkan semua tugas.
/{BotCommands.ListCommand[0]} atau /{BotCommands.ListCommand[1]} [query] : Mencari file/folder di Google Drive.
/{BotCommands.SearchCommand[0]} atau /{BotCommands.SearchCommand[1]} [query] : Mencari torrent menggunakan API.
/{BotCommands.StatusCommand[0]} atau /{BotCommands.StatusCommand[1]} : Menampilkan status dari semua tugas yang sedang berjalan.
/{BotCommands.StatsCommand[0]} atau /{BotCommands.StatsCommand[1]} : Menampilan statistik dari mesin bot.
/{BotCommands.PingCommand[0]} atau /{BotCommands.PingCommand[1]} : Mengetes respon bot (Hanya Owner & Sudo).
/{BotCommands.AuthorizeCommand[0]} atau /{BotCommands.AuthorizeCommand[1]} : Memberikan izin chat atau user untuk menggunakan bot (Hanya Owner & Sudo).
/{BotCommands.UnAuthorizeCommand[0]} atau /{BotCommands.UnAuthorizeCommand[1]} : Menghapus izin chat atau user untuk menggunakan bot (Hanya Owner & Sudo).
/{BotCommands.UsersCommand[0]} atau /{BotCommands.UsersCommand[1]} : Menampilan pengaturan User (Hanya Owner & Sudo).
/{BotCommands.AddSudoCommand[0]} atau /{BotCommands.AddSudoCommand[1]} : Menambahkan User Sudo (Hanya Owner).
/{BotCommands.RmSudoCommand[0]} atau /{BotCommands.RmSudoCommand[1]} : Menghapus User Sudo (Hanya Owner).
/{BotCommands.RestartCommand[0]} atau /{BotCommands.RestartCommand[1]} : Memulai ulang dan memperbarui bot (Hanya Owner & Sudo).
/{BotCommands.LogCommand[0]} atau /{BotCommands.LogCommand[1]} : Mengambil log file dari bot (Hanya Owner & Sudo).
/{BotCommands.ShellCommand[0]} atau /{BotCommands.ShellCommand[1]} : Menjalankan perintah Shell (Hanya Owner).
/{BotCommands.EvalCommand[0]} atau /{BotCommands.EvalCommand[1]} : Menjalankan perintah Kode Python (Hanya Owner).
/{BotCommands.ExecCommand[0]} atau /{BotCommands.ExecCommand[1]} : Menjalankan perintah Exec (Hanya Owner).
/{BotCommands.ClearLocalsCommand[0]} atau /{BotCommands.ClearLocalsCommand[1]} : Menghapus penyimpanan lokal (Hanya Owner)
/{BotCommands.RssCommand} : Menu RSS.

NOTE : Kirim perintah tanpa argument untuk melihat perintah secara detail!
'''


async def bot_help(_, message):
    await sendMessage(message, help_string)


async def restart_notification():
    if await aiopath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
    else:
        chat_id, msg_id = 0, 0

    async def send_incompelete_task_message(cid, msg):
        try:
            if msg.startswith('Bot berhasil dimulai ulang!'):
                await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=msg)
                await aioremove(".restartmsg")
            else:
                await bot.send_message(chat_id=cid, text=msg, disable_web_page_preview=True,
                                       disable_notification=True)
        except Exception as e:
            LOGGER.error(e)

    now = datetime.now(timezone(f'Asia/Makassar'))
    if INCOMPLETE_TASK_NOTIFIER and DATABASE_URL:
        if notifier_dict := await DbManger().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                msg = f"""{'Bot berhasil dimulai ulang!' if cid == chat_id else 'Bot dimulai ulang!'}
<pre languange="bash">
<b>Hari      :</b> <code>{now.strftime('%A')}</code>
<b>Tanggal   :</b> <code>{now.strftime('%d %B %Y')}</code>
<b>Waktu     :</b> <code>{now.strftime('%H:%M:%S WIB')}</code>
<b>Quotes    :</b>
<code>{get_quotes()}</code>
</pre>           
"""
                if data.items():
                    msg += f"\n<b>Tugas yang belum selesai :</b>"
                for tag, links in data.items():
                    msg += f"\n{tag} :"
                    for index, link in enumerate(links, start=1):
                        msg += f"\n <a href='{link}'>Tugas ke {index}</a>"
                        if len(msg.encode()) > 4000:
                            await send_incompelete_task_message(cid, msg)
                            msg = ''
                if msg:
                    await send_incompelete_task_message(cid, msg)

    if await aiopath.isfile(".restartmsg"):
        try:
            msg = f"""Bot berhasil dimulai ulang!
<pre languange="bash">
<b>Hari      :</b> <code>{now.strftime('%A')}</code>
<b>Tanggal   :</b> <code>{now.strftime('%d %B %Y')}</code>
<b>Waktu     :</b> <code>{now.strftime('%H:%M:%S WIB')}</code>
<b>Quotes    :</b>
<code>{get_quotes()}</code>
</pre>           
"""
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=msg)
        except:
            pass
        await aioremove(".restartmsg")


async def main():
    await gather(start_cleanup(), torrent_search.initiate_search_tools(), restart_notification())
    await sync_to_async(start_aria2_listener, wait=False)
    bot.add_handler(MessageHandler(
        start, filters=command(BotCommands.StartCommand)))
    bot.add_handler(MessageHandler(log, filters=command(
        BotCommands.LogCommand) & CustomFilters.sudo))
    bot.add_handler(MessageHandler(restart, filters=command(
        BotCommands.RestartCommand) & CustomFilters.sudo))
    bot.add_handler(MessageHandler(ping, filters=command(
        BotCommands.PingCommand) & CustomFilters.authorized))
    bot.add_handler(MessageHandler(bot_help, filters=command(
        BotCommands.HelpCommand) & CustomFilters.authorized))
    bot.add_handler(MessageHandler(stats, filters=command(
        BotCommands.StatsCommand) & CustomFilters.authorized))
    LOGGER.info(f"Bot Started! => @{bot.me.username}")
    signal(SIGINT, exit_clean_up)

bot.loop.run_until_complete(main())
bot.loop.run_forever()
