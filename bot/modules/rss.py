from apscheduler.triggers.interval import IntervalTrigger
from asyncio import Lock, sleep
from datetime import datetime, timedelta, timezone
from feedparser import parse as feedparse
from functools import partial
from httpx import AsyncClient
from io import BytesIO
from pyrogram.filters import command, regex, create
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from re import sub as re_sub, findall as re_findall
from time import time

from bot import scheduler, rss_dict, LOGGER, DATABASE_URL, config_dict, bot
from bot.helper.ext_utils.bot_utils import new_thread, arg_parser
from bot.helper.ext_utils.db_handler import DbManager
from bot.helper.ext_utils.exceptions import RssShutdownException
from bot.helper.ext_utils.help_messages import RSS_HELP_MESSAGE
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import (
    sendMessage,
    editMessage,
    sendFile,
    deleteMessage,
    customSendRss,
)


rss_dict_lock = Lock()
handler_dict = {}


async def rssMenu(event):
    user_id = event.from_user.id
    buttons = ButtonMaker()
    buttons.ibutton("Subscribe", f"rss sub {user_id}")
    buttons.ibutton("Subscriptions", f"rss list {user_id} 0")
    buttons.ibutton("Get Items", f"rss get {user_id}")
    buttons.ibutton("Edit", f"rss edit {user_id}")
    buttons.ibutton("Pause", f"rss pause {user_id}")
    buttons.ibutton("Resume", f"rss resume {user_id}")
    buttons.ibutton("Unsubscribe", f"rss unsubscribe {user_id}")
    if await CustomFilters.sudo("", event):
        buttons.ibutton("All Subscriptions", f"rss listall {user_id} 0")
        buttons.ibutton("Pause All", f"rss allpause {user_id}")
        buttons.ibutton("Resume All", f"rss allresume {user_id}")
        buttons.ibutton("Unsubscribe All", f"rss allunsub {user_id}")
        buttons.ibutton("Delete User", f"rss deluser {user_id}")
        if scheduler.running:
            buttons.ibutton("Shutdown Rss", f"rss shutdown {user_id}")
        else:
            buttons.ibutton("Start Rss", f"rss start {user_id}")
    buttons.ibutton("Close", f"rss close {user_id}")
    button = buttons.build_menu(2)
    msg = f"Rss Menu | Users: {len(rss_dict)} | Running: {scheduler.running}"
    return msg, button


async def updateRssMenu(query):
    msg, button = await rssMenu(query)
    await editMessage(query.message, msg, button)


async def getRssMenu(_, message):
    msg, button = await rssMenu(message)
    await sendMessage(message, msg, button)


async def rssSub(_, message, pre_event):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    if username := message.from_user.username:
        tag = f"@{username}"
    else:
        tag = message.from_user.mention
    msg = ""
    items = message.text.split("\n")
    for index, item in enumerate(items, start=1):
        args = item.split()
        if len(args) < 2:
            await sendMessage(
                message,
                f"<code>{item}</code> <b>Format Salah! Baca pesan bantuan sebelum menambahkan langganan RSS baru!</b>",
            )
            continue
        title = args[0].strip()
        if (user_feeds := rss_dict.get(user_id, False)) and title in user_feeds:
            await sendMessage(
                message, f"<b>RSS dengan Judul</b> <code>{title}</code> <b>telah ditambahkan!</b>"
            )
            continue
        feed_link = args[1].strip()
        if feed_link.startswith(("-inf", "-exf", "-c")):
            await sendMessage(
                message,
                f"<b>Terdapat kesalahan pada line<b> <code>{index}</code>! <b>Tambahkan Judul sesuai dengan contoh!</b>",
            )
            continue
        inf_lists = []
        exf_lists = []
        if len(args) > 2:
            arg_base = {"-c": None, "-inf": None, "-exf": None, "-stv": None}
            arg_parser(args[2:], arg_base)
            cmd = arg_base["-c"]
            inf = arg_base["-inf"]
            exf = arg_base["-exf"]
            stv = arg_base["-stv"]
            if stv is not None:
                stv = stv.lower() == "true"
            if inf is not None:
                filters_list = inf.split("|")
                for x in filters_list:
                    y = x.split(" or ")
                    inf_lists.append(y)
            if exf is not None:
                filters_list = exf.split("|")
                for x in filters_list:
                    y = x.split(" or ")
                    exf_lists.append(y)
        else:
            inf = None
            exf = None
            cmd = None
            stv = False
        try:
            async with AsyncClient(verify=False) as client:
                res = await client.get(feed_link)
            html = res.text
            rss_d = feedparse(html)
            last_title = rss_d.entries[0]["title"]
            msg += "<b>Berlangganan!</b>"
            msg += f"\n<b>Judul :</b> <code>{title}</code>\n<b>URL Feed :</b> <code>{feed_link}</code>"
            msg += f"\n<b>Item Terakhir untuk judul</b> <code>{rss_d.feed.title}</code>:"
            msg += (
                f"\n<b>Nama :</b> <code>{last_title.replace('>', '').replace('<', '')}</code>"
            )
            try:
                last_link = rss_d.entries[0]["links"][1]["href"]
            except IndexError:
                last_link = rss_d.entries[0]["link"]
            msg += f"\n<b>Link :</b> <code>{last_link}</code>"
            msg += f"\n<b>Perintah :</b> <code>{cmd}</code>"
            msg += (
                f"\n<b>Filter:</b>\n<b>Inf :</b> <code>{inf}</code>\n<b>Exf :</b> <code>{exf}</code>\n<b>Sensitive :</b> <code>{stv}</code>"
            )
            async with rss_dict_lock:
                if rss_dict.get(user_id, False):
                    rss_dict[user_id][title] = {
                        "link": feed_link,
                        "last_feed": last_link,
                        "last_title": last_title,
                        "inf": inf_lists,
                        "exf": exf_lists,
                        "paused": False,
                        "command": cmd,
                        "sensitive": stv,
                        "tag": tag,
                    }
                else:
                    rss_dict[user_id] = {
                        title: {
                            "link": feed_link,
                            "last_feed": last_link,
                            "last_title": last_title,
                            "inf": inf_lists,
                            "exf": exf_lists,
                            "paused": False,
                            "command": cmd,
                            "sensitive": stv,
                            "tag": tag,
                        }
                    }
            LOGGER.info(
                f"Rss Feed Added: id: {user_id} - title: {title} - link: {feed_link} - c: {cmd} - inf: {inf} - exf: {exf} - stv {stv}"
            )
        except (IndexError, AttributeError) as e:
            emsg = f"<b>Link</b> <code>{feed_link}</code> <b>sepertinya bukan RSS Feed atau Bot diblokir oleh RSS!</b>"
            await sendMessage(message, emsg + "\nError: " + str(e))
        except Exception as e:
            await sendMessage(message, str(e))
    if msg:
        if DATABASE_URL and rss_dict[user_id]:
            await DbManager().rss_update(user_id)
        await sendMessage(message, msg)
        is_sudo = await CustomFilters.sudo("", message)
        if scheduler.state == 2:
            scheduler.resume()
        elif is_sudo and not scheduler.running:
            addJob()
            scheduler.start()
    await updateRssMenu(pre_event)


async def getUserId(title):
    async with rss_dict_lock:
        return next(
            (
                (True, user_id)
                for user_id, feed in list(rss_dict.items())
                if feed["title"] == title
            ),
            (False, False),
        )


async def rssUpdate(_, message, pre_event, state):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    titles = message.text.split()
    is_sudo = await CustomFilters.sudo("", message)
    updated = []
    for title in titles:
        title = title.strip()
        if not (res := rss_dict[user_id].get(title, False)):
            if is_sudo:
                res, user_id = await getUserId(title)
            if not res:
                user_id = message.from_user.id
                await sendMessage(message, f"{title} not found!")
                continue
        istate = rss_dict[user_id][title].get("paused", False)
        if istate and state == "pause" or not istate and state == "resume":
            await sendMessage(message, f"{title} already {state}d!")
            continue
        async with rss_dict_lock:
            updated.append(title)
            if state == "unsubscribe":
                del rss_dict[user_id][title]
            elif state == "pause":
                rss_dict[user_id][title]["paused"] = True
            elif state == "resume":
                rss_dict[user_id][title]["paused"] = False
        if state == "resume":
            if scheduler.state == 2:
                scheduler.resume()
            elif is_sudo and not scheduler.running:
                addJob()
                scheduler.start()
        if is_sudo and DATABASE_URL and user_id != message.from_user.id:
            await DbManager().rss_update(user_id)
        if not rss_dict[user_id]:
            async with rss_dict_lock:
                del rss_dict[user_id]
            if DATABASE_URL:
                await DbManager().rss_delete(user_id)
                if not rss_dict:
                    await DbManager().trunc_table("rss")
    if updated:
        LOGGER.info(f"Rss link with Title(s): {updated} has been {state}d!")
        await sendMessage(
            message,
            f"<b>RSS dengan judul</b> <code>{updated}</code> <b>telah</b> <code>di{state}d</code>!"
        )
        if DATABASE_URL and rss_dict.get(user_id):
            await DbManager().rss_update(user_id)
    await updateRssMenu(pre_event)


async def rssList(query, start, all_users=False):
    user_id = query.from_user.id
    buttons = ButtonMaker()
    if all_users:
        list_feed = f"<b>All subscriptions | Page: {int(start/5)} </b>"
        async with rss_dict_lock:
            keysCount = sum(len(v.keys()) for v in list(rss_dict.values()))
            index = 0
            for titles in list(rss_dict.values()):
                for index, (title, data) in enumerate(
                    list(titles.items())[start : 5 + start]
                ):
                    list_feed += f"\n\n<b>Title:</b> <code>{title}</code>\n"
                    list_feed += f"<b>Feed Url:</b> <code>{data['link']}</code>\n"
                    list_feed += f"<b>Command:</b> <code>{data['command']}</code>\n"
                    list_feed += f"<b>Inf:</b> <code>{data['inf']}</code>\n"
                    list_feed += f"<b>Exf:</b> <code>{data['exf']}</code>\n"
                    list_feed += f"<b>Sensitive:</b> <code>{data.get('sensitive', False)}</code>\n"
                    list_feed += f"<b>Paused:</b> <code>{data['paused']}</code>\n"
                    list_feed += f"<b>User:</b> {data['tag'].replace('@', '', 1)}"
                    index += 1
                    if index == 5:
                        break
    else:
        list_feed = f"<b>Your subscriptions | Page: {int(start/5)} </b>"
        async with rss_dict_lock:
            keysCount = len(rss_dict.get(user_id, {}).keys())
            for title, data in list(rss_dict[user_id].items())[start : 5 + start]:
                list_feed += f"\n\n<b>Title:</b> <code>{title}</code>\n<b>Feed Url: </b><code>{data['link']}</code>\n"
                list_feed += f"<b>Command:</b> <code>{data['command']}</code>\n"
                list_feed += f"<b>Inf:</b> <code>{data['inf']}</code>\n"
                list_feed += f"<b>Exf:</b> <code>{data['exf']}</code>\n"
                list_feed += f"<b>Sensitive:</b> <code>{data.get('sensitive', False)}</code>\n"
                list_feed += f"<b>Paused:</b> <code>{data['paused']}</code>\n"
    buttons.ibutton("Back", f"rss back {user_id}")
    buttons.ibutton("Close", f"rss close {user_id}")
    if keysCount > 5:
        for x in range(0, keysCount, 5):
            buttons.ibutton(
                f"{int(x / 5)}", f"rss list {user_id} {x}", position="footer"
            )
    button = buttons.build_menu(2)
    if query.message.text.html == list_feed:
        return
    await editMessage(query.message, list_feed, button)


async def rssGet(_, message, pre_event):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    args = message.text.split()
    if len(args) < 2:
        await sendMessage(
            message,
            f"<code>{args}</code> <b>Format Salah! Baca pesan bantuan!</b>",
        )
        await updateRssMenu(pre_event)
        return
    try:
        title = args[0]
        count = int(args[1])
        data = rss_dict[user_id].get(title, False)
        if data and count > 0:
            try:
                msg = await sendMessage(
                    message, f"Getting the last <b>{count}</b> item(s) from {title}"
                )
                async with AsyncClient(verify=False) as client:
                    res = await client.get(data["link"])
                html = res.text
                rss_d = feedparse(html)
                item_info = ""
                for item_num in range(count):
                    try:
                        link = rss_d.entries[item_num]["links"][1]["href"]
                    except IndexError:
                        link = rss_d.entries[item_num]["link"]
                    item_info += f"<b>Name: </b><code>{rss_d.entries[item_num]['title'].replace('>', '').replace('<', '')}</code>\n"
                    item_info += f"<b>Link: </b><code>{link}</code>\n\n"
                item_info_ecd = item_info.encode()
                if len(item_info_ecd) > 4000:
                    with BytesIO(item_info_ecd) as out_file:
                        out_file.name = f"rssGet {title} items_no. {count}.txt"
                        await sendFile(message, out_file)
                    await deleteMessage(msg)
                else:
                    await editMessage(msg, item_info)
            except IndexError as e:
                LOGGER.error(str(e))
                await editMessage(
                    msg, "<b>Limit terlampaui, coba lagi menggunakan nilai yang lebih rendah!</b>"
                )
            except Exception as e:
                LOGGER.error(str(e))
                await editMessage(msg, str(e))
        else:
            await sendMessage(message, "<b>Judul tidak ditemukan!</b>")
    except Exception as e:
        LOGGER.error(str(e))
        await sendMessage(message, f"<b>Tambahkan nilai valid!</b>\n<code>{e}</code>")
    await updateRssMenu(pre_event)


async def rssEdit(_, message, pre_event):
    user_id = message.from_user.id
    handler_dict[user_id] = False
    items = message.text.split("\n")
    updated = False
    for item in items:
        args = item.split()
        title = args[0].strip()
        if len(args) < 2:
            await sendMessage(
                message,
                f"<code>{item}</code> <b>Format Salah! Baca pesan bantuan!</b>",
            )
            continue
        elif not rss_dict[user_id].get(title, False):
            await sendMessage(message, "<b>Judul tidak ditemukan!</b>")
            continue
        updated = True
        inf_lists = []
        exf_lists = []
        arg_base = {"-c": None, "-inf": None, "-exf": None, "-stv": None}
        arg_parser(args[1:], arg_base)
        cmd = arg_base["-c"]
        inf = arg_base["-inf"]
        exf = arg_base["-exf"]
        stv = arg_base["-stv"]
        async with rss_dict_lock:
            if stv is not None:
                stv = stv.lower() == "true"
                rss_dict[user_id][title]["sensitive"] = stv
            if cmd is not None:
                if cmd.lower() == "none":
                    cmd = None
                rss_dict[user_id][title]["command"] = cmd
            if inf is not None:
                if inf.lower() != "none":
                    filters_list = inf.split("|")
                    for x in filters_list:
                        y = x.split(" or ")
                        inf_lists.append(y)
                rss_dict[user_id][title]["inf"] = inf_lists
            if exf is not None:
                if exf.lower() != "none":
                    filters_list = exf.split("|")
                    for x in filters_list:
                        y = x.split(" or ")
                        exf_lists.append(y)
                rss_dict[user_id][title]["exf"] = exf_lists
    if DATABASE_URL and updated:
        await DbManager().rss_update(user_id)
    await updateRssMenu(pre_event)


async def rssDelete(_, message, pre_event):
    handler_dict[message.from_user.id] = False
    users = message.text.split()
    for user in users:
        user = int(user)
        async with rss_dict_lock:
            del rss_dict[user]
        if DATABASE_URL:
            await DbManager().rss_delete(user)
    await updateRssMenu(pre_event)


async def event_handler(client, query, pfunc):
    user_id = query.from_user.id
    handler_dict[user_id] = True
    start_time = time()

    async def event_filter(_, __, event):
        user = event.from_user or event.sender_chat
        return bool(
            user.id == user_id and event.chat.id == query.message.chat.id and event.text
        )

    handler = client.add_handler(MessageHandler(pfunc, create(event_filter)), group=-1)
    while handler_dict[user_id]:
        await sleep(0.5)
        if time() - start_time > 60:
            handler_dict[user_id] = False
            await updateRssMenu(query)
    client.remove_handler(*handler)


@new_thread
async def rssListener(client, query):
    user_id = query.from_user.id
    message = query.message
    data = query.data.split()
    if int(data[2]) != user_id and not await CustomFilters.sudo("", query):
        await query.answer(
            text="You don't have permission to use these buttons!", show_alert=True
        )
    elif data[1] == "close":
        await query.answer()
        handler_dict[user_id] = False
        await deleteMessage(message.reply_to_message)
        await deleteMessage(message)
    elif data[1] == "back":
        await query.answer()
        handler_dict[user_id] = False
        await updateRssMenu(query)
    elif data[1] == "sub":
        await query.answer()
        handler_dict[user_id] = False
        buttons = ButtonMaker()
        buttons.ibutton("Back", f"rss back {user_id}")
        buttons.ibutton("Close", f"rss close {user_id}")
        button = buttons.build_menu(2)
        await editMessage(message, RSS_HELP_MESSAGE, button)
        pfunc = partial(rssSub, pre_event=query)
        await event_handler(client, query, pfunc)
    elif data[1] == "list":
        handler_dict[user_id] = False
        if len(rss_dict.get(int(data[2]), {})) == 0:
            await query.answer(text="No subscriptions!", show_alert=True)
        else:
            await query.answer()
            start = int(data[3])
            await rssList(query, start)
    elif data[1] == "get":
        handler_dict[user_id] = False
        if len(rss_dict.get(int(data[2]), {})) == 0:
            await query.answer(text="No subscriptions!", show_alert=True)
        else:
            await query.answer()
            buttons = ButtonMaker()
            buttons.ibutton("Back", f"rss back {user_id}")
            buttons.ibutton("Close", f"rss close {user_id}")
            button = buttons.build_menu(2)
            await editMessage(
                message,
                "Send one title with value separated by space get last X items.\nTitle Value\nTimeout: 60 sec.",
                button,
            )
            pfunc = partial(rssGet, pre_event=query)
            await event_handler(client, query, pfunc)
    elif data[1] in ["unsubscribe", "pause", "resume"]:
        handler_dict[user_id] = False
        if len(rss_dict.get(int(data[2]), {})) == 0:
            await query.answer(text="No subscriptions!", show_alert=True)
        else:
            await query.answer()
            buttons = ButtonMaker()
            buttons.ibutton("Back", f"rss back {user_id}")
            if data[1] == "pause":
                buttons.ibutton("Pause AllMyFeeds", f"rss uallpause {user_id}")
            elif data[1] == "resume":
                buttons.ibutton("Resume AllMyFeeds", f"rss uallresume {user_id}")
            elif data[1] == "unsubscribe":
                buttons.ibutton("Unsub AllMyFeeds", f"rss uallunsub {user_id}")
            buttons.ibutton("Close", f"rss close {user_id}")
            button = buttons.build_menu(2)
            await editMessage(
                message,
                f"Send one or more rss titles separated by space to {data[1]}.\nTimeout: 60 sec.",
                button,
            )
            pfunc = partial(rssUpdate, pre_event=query, state=data[1])
            await event_handler(client, query, pfunc)
    elif data[1] == "edit":
        handler_dict[user_id] = False
        if len(rss_dict.get(int(data[2]), {})) == 0:
            await query.answer(text="No subscriptions!", show_alert=True)
        else:
            await query.answer()
            buttons = ButtonMaker()
            buttons.ibutton("Back", f"rss back {user_id}")
            buttons.ibutton("Close", f"rss close {user_id}")
            button = buttons.build_menu(2)
            msg = """Send one or more rss titles with new filters or command separated by new line.
Examples:
Title1 -c mirror -up remote:path/subdir -exf none -inf 1080 or 720 -stv true
Title2 -c none -inf none -stv false
Title3 -c mirror -rcf xxx -up xxx -z pswd -stv false
Note: Only what you provide will be edited, the rest will be the same like example 2: exf will stay same as it is.
Timeout: 60 sec. Argument -c for command and arguments
            """
            await editMessage(message, msg, button)
            pfunc = partial(rssEdit, pre_event=query)
            await event_handler(client, query, pfunc)
    elif data[1].startswith("uall"):
        handler_dict[user_id] = False
        if len(rss_dict.get(int(data[2]), {})) == 0:
            await query.answer(text="No subscriptions!", show_alert=True)
            return
        await query.answer()
        if data[1].endswith("unsub"):
            async with rss_dict_lock:
                del rss_dict[int(data[2])]
            if DATABASE_URL:
                await DbManager().rss_delete(int(data[2]))
            await updateRssMenu(query)
        elif data[1].endswith("pause"):
            async with rss_dict_lock:
                for title in list(rss_dict[int(data[2])].keys()):
                    rss_dict[int(data[2])][title]["paused"] = True
            if DATABASE_URL:
                await DbManager().rss_update(int(data[2]))
        elif data[1].endswith("resume"):
            async with rss_dict_lock:
                for title in list(rss_dict[int(data[2])].keys()):
                    rss_dict[int(data[2])][title]["paused"] = False
            if scheduler.state == 2:
                scheduler.resume()
            if DATABASE_URL:
                await DbManager().rss_update(int(data[2]))
        await updateRssMenu(query)
    elif data[1].startswith("all"):
        if len(rss_dict) == 0:
            await query.answer(text="No subscriptions!", show_alert=True)
            return
        await query.answer()
        if data[1].endswith("unsub"):
            async with rss_dict_lock:
                rss_dict.clear()
            if DATABASE_URL:
                await DbManager().trunc_table("rss")
            await updateRssMenu(query)
        elif data[1].endswith("pause"):
            async with rss_dict_lock:
                for user in list(rss_dict.keys()):
                    for title in list(rss_dict[user].keys()):
                        rss_dict[int(data[2])][title]["paused"] = True
            if scheduler.running:
                scheduler.pause()
            if DATABASE_URL:
                await DbManager().rss_update_all()
        elif data[1].endswith("resume"):
            async with rss_dict_lock:
                for user in list(rss_dict.keys()):
                    for title in list(rss_dict[user].keys()):
                        rss_dict[int(data[2])][title]["paused"] = False
            if scheduler.state == 2:
                scheduler.resume()
            elif not scheduler.running:
                addJob()
                scheduler.start()
            if DATABASE_URL:
                await DbManager().rss_update_all()
    elif data[1] == "deluser":
        if len(rss_dict) == 0:
            await query.answer(text="No subscriptions!", show_alert=True)
        else:
            await query.answer()
            buttons = ButtonMaker()
            buttons.ibutton("Back", f"rss back {user_id}")
            buttons.ibutton("Close", f"rss close {user_id}")
            button = buttons.build_menu(2)
            msg = "Send one or more user_id separated by space to delete their resources.\nTimeout: 60 sec."
            await editMessage(message, msg, button)
            pfunc = partial(rssDelete, pre_event=query)
            await event_handler(client, query, pfunc)
    elif data[1] == "listall":
        if not rss_dict:
            await query.answer(text="No subscriptions!", show_alert=True)
        else:
            await query.answer()
            start = int(data[3])
            await rssList(query, start, all_users=True)
    elif data[1] == "shutdown":
        if scheduler.running:
            await query.answer()
            scheduler.shutdown(wait=False)
            await sleep(0.5)
            await updateRssMenu(query)
        else:
            await query.answer(text="Already Stopped!", show_alert=True)
    elif data[1] == "start":
        if not scheduler.running:
            await query.answer()
            addJob()
            scheduler.start()
            await updateRssMenu(query)
        else:
            await query.answer(text="Already Running!", show_alert=True)


async def rssMonitor():
    if not config_dict["RSS_CHAT_ID"]:
        LOGGER.warning("RSS_CHAT_ID not added! Shutting down rss scheduler...")
        scheduler.shutdown(wait=False)
        return
    if len(rss_dict) == 0:
        scheduler.pause()
        return
    all_paused = True
    for user, items in list(rss_dict.items()):
        for title, data in list(items.items()):
            try:
                if data["paused"]:
                    continue
                tries = 0
                while True:
                    try:
                        async with AsyncClient(verify=False) as client:
                            res = await client.get(data["link"])
                        html = res.text
                        break
                    except:
                        tries += 1
                        if tries > 3:
                            raise
                        continue
                rss_d = feedparse(html)
                try:
                    last_link = rss_d.entries[0]["links"][1]["href"]
                except IndexError:
                    last_link = rss_d.entries[0]["link"]
                finally:
                    all_paused = False
                last_title = rss_d.entries[0]["title"]
                if data["last_feed"] == last_link or data["last_title"] == last_title:
                    continue
                feed_count = 0
                while True:
                    try:
                        await sleep(10)
                    except:
                        raise RssShutdownException("Rss Monitor Stopped!")
                    try:
                        item_title = rss_d.entries[feed_count]["title"]
                        try:
                            url = rss_d.entries[feed_count]["links"][1]["href"]
                        except IndexError:
                            url = rss_d.entries[feed_count]["link"]
                        view = None
                        size = rss_d.entries[feed_count].get("size")
                        category = rss_d.entries[feed_count].get("category")
                        description = rss_d.entries[feed_count].get("description")
                        published_date = rss_d.entries[feed_count].get("published")
                        
                        if data["last_feed"] == url or data["last_title"] == item_title:
                            break
                    except IndexError:
                        LOGGER.warning(
                            f"Reached Max index no. {feed_count} for this feed: {title}. Maybe you need to use less RSS_DELAY to not miss some torrents"
                        )
                        break
                    parse = True
                    for flist in data["inf"]:
                        if (
                            data.get("sensitive", False)
                            and all(x.lower() not in item_title.lower() for x in flist)
                        ) or (
                            not data.get("sensitive", False)
                            and all(x not in item_title for x in flist)
                        ):
                            parse = False
                            feed_count += 1
                            break
                    if not parse:
                        continue
                    for flist in data["exf"]:
                        if (
                            data.get("sensitive", False)
                            and any(x.lower() in item_title.lower() for x in flist)
                        ) or (
                            data.get("sensitive", False)
                            and any(x in item_title for x in flist)
                        ):
                            parse = False
                            feed_count += 1
                            break
                    if not parse:
                        continue
                    if command := data["command"]:
                        cmd = command.split(maxsplit=1)
                        cmd.insert(1, url)
                        feed_msg = " ".join(cmd)
                        if not feed_msg.startswith("/"):
                            feed_msg = f"/{feed_msg}"
                    else:
                        image = None
                        image_caption = None
                        
                        p2p_group = None
                        not_tracker = False
                        private_tracker = False
                        
                        item_title = item_title.replace(">", "").replace("<", "")

                        # BlackListed p2p_group / p2p_name (Based on my RSS Feed)
                        blacklist = [
                            "-", "a", "ass", "activated", "audio", "audios", "audiobook", "br", "chan", "compilation", "dl",
                            "dlrip", "empire", "en", "eng", "flac", "global", "hd", "hen", "i", "id", "in", "jap", "kaime", 
                            "kun", "la", "man", "media", "off", "pot", "raw", "raws", "ray",  "rayrip", "res", "rip", "sai", 
                            "sama", "san", "srt", "sub", "subs", "subtitle", "true", "us", "x", "2160", "1080", "720", "480",
                            "360", "2160p", "1080p", "720p", "480p", "360p", "1080p-avc", "1080p-hevc", "1080p-av1", "1080p-vp9", 
                            "720p-avc", "720p-hevc", "720p-av1", "720p-vp9"
                        ]
                        
                        if (
                            p2p_group is None
                            and "-" in item_title
                        ):
                            p2p_group = re_findall(r"\-([0-9a-zA-Z\-]+)", item_title)
                            if len(p2p_group) != 0:
                                p2p_group = p2p_group[-1]
                                if (
                                    isinstance(p2p_group, str)
                                    and (not p2p_group.isdigit())
                                    and p2p_group.lower() not in blacklist
                                ):
                                    p2p_group = p2p_group
                                else:
                                    p2p_group = None
                            else:
                                p2p_group = None
                        
                        if (
                            p2p_group is None
                            and "[" in item_title
                            and "]" in item_title
                        ):
                            p2p_group = re_findall(r"\[([0-9a-zA-Z\-\.]+)\]", item_title)
                            if len(p2p_group) != 0:
                                p2p_group = p2p_group[0]
                                if (
                                    isinstance(p2p_group, str)
                                    and (not p2p_group.isdigit())
                                    and p2p_group.lower() not in blacklist
                                ):
                                    p2p_group = p2p_group
                                else:
                                    p2p_group = None
                            else:
                                p2p_group = None
                        
                        # Some Groups which using - and . character is not detected as Tag (#)
                        if (
                            p2p_group is not None
                            and "-" in p2p_group
                        ):
                            p2p_group = p2p_group.replace("-", "_")

                        if (
                            p2p_group is not None
                            and "." in p2p_group
                        ):
                            p2p_group = p2p_group.replace(".", "")
                        
                        if str(p2p_group).isdigit():
                            p2p_group = None


                        # Add Your custom RSS feed here
                        # https://nyaa.si/ or https://sukebei.nyaa.si/
                        if "nyaa" in url.lower():
                            view = rss_d.entries[feed_count].get("id")
                            size = rss_d.entries[feed_count].get("nyaa_size")
                            category = rss_d.entries[feed_count].get("nyaa_category")
                            description = f"""<b>Remake :</b> <code>{rss_d.entries[feed_count].get('nyaa_remake')}</code> | <b>Trusted :</b> <code>{rss_d.entries[feed_count].get('nyaa_trusted')}</code>

<b>Seed :</b> <code>{rss_d.entries[feed_count].get('nyaa_seeders')}</code> | <b>Leech :</b> <code>{rss_d.entries[feed_count].get('nyaa_leechers')}</code> | <b>Completed :</b> <code>{rss_d.entries[feed_count].get('nyaa_downloads')}</code>

<b>Hash :</b>
<code>{rss_d.entries[feed_count].get('nyaa_infohash')}</code>"""
                        
                        # https://ouo.si/
                        elif "ouo" in url.lower():
                            view = rss_d.entries[feed_count].get("id")
                            if not category:
                                category = "Anime"
                            description = re_sub(r"<.*?>", "", description).replace("\n", "")
                            description = f"""<b>CRC32 :</b> <code>{description.split('CRC32: ')[1].split('MediaInfo')[0]}</code>

<b>BitRate :</b> <code>{description.split('Overall Bit Rate: ')[1].split('Subtitle: ')[0]}</code>

<b>Duration :</b> <code>{description.split('Duration: ')[1].split('CRC32: ')[0]}</code>

<b>Subtitle :</b> <code>{description.split('Subtitle: ')[1].split('Duration: ')[0]}</code>"""
                        
                        # https://bangumi.moe/
                        elif "bangumi" in url.lower():
                            image = re_findall(r"\bhttps?://\S+?\.(?:png|jpe?g)\b", description)[0]
                            if not category:
                                category = "Anime"
                            description = None

                        # https://tgx.rs/
                        elif "watercache" in url.lower():
                            view = rss_d.entries[feed_count].get("comments")
                            if description:
                                size = description.split("Size: ")[-1].split(" Added:")[0]
                            description = None
                        
                        # https://yts.mx/
                        elif "yts" in url.lower():
                            view = rss_d.entries[feed_count].get("guid")
                            if description:
                                image = re_findall(r"\bhttps?://\S+?\.(?:png|jpe?g)\b", description)[0]
                                description = re_sub(r"<.*?>", "", description)
                                size = description.split("Size: ")[-1].split("Runtime: ")[0]
                                category = description.split("Genre: ")[-1].split("Size: ")[0].replace(" /", ",")
                                description = rss_d.entries[feed_count].get("description").split("<br />")[-1]
                            if image:
                                image_caption = item_title
                        
                        # https://avistaz.to/
                        elif "avistaz" in url.lower():
                            private_tracker = True
                            url = "https://avistaz.to/"
                            view = rss_d.entries[feed_count]["link"]
                            if description:
                                description = re_sub(r"<.*?>", "", description)
                                size = description.split("Size: ")[-1].split("Uploaded: ")[0]
                                description = f"""<b>Seed :</b> <code>{description.split("Seed: ")[-1].split(" |")[0]}</code> | <b>Leech :</b> <code>{description.split("Leech: ")[-1].split(" |")[0]}</code> | <b>Completed :</b> <code>{description.split("Completed: ")[-1].split("Uploader: ")[0]}</code>

<b>Oleh :</b> <code>{description.split("Uploader: ")[-1].split("Rip Type: ")[0]}</code>"""

                        # https://www.torrentleech.org/
                        elif "torrentleech" in url.lower():
                            private_tracker = True
                            url = "https://www.torrentleech.org/"
                            view = rss_d.entries[feed_count].get("guid")
                            description = f"""<b>Seed :</b> <code>{description.split('Seeders: ', 1)[-1].split(' ')[0]}</code> | <b>Leech :</b> <code>{description.split('Leechers: ', 1)[-1].split(' ')[0]}</code>"""
                        
                        # https://psa.wf/
                        elif "psa" in url.lower():
                            not_tracker = True
                            view = url
                            category = ", ".join(x["term"] for x in rss_d.entries[feed_count].get("tags"))
                            if description:
                                image = re_findall(r"\bhttps?://\S+?\.(?:png|jpe?g)\b", description)[0]
                                description = re_sub(r"<.*?>", "", description)
                            if image:
                                image_caption = item_title
                        
                        # https://pahe.ink/
                        elif "pahe" in url.lower():
                            not_tracker = True
                            view = url
                            category = ", ".join(x["term"] for x in rss_d.entries[feed_count].get("tags"))
                        
                        # https://hdencode.ro/
                        elif "hdencode" in url.lower():
                            not_tracker = True
                            view = url
                            # Manually get categories from title when set rss subscription on bot.
                            # Example: the title is HDEncode_Movies so the category will be Movies
                            category = title.split("_", 1)[-1].replace("_", " ") 
                            size = item_title.split(" – ")[-1]
                            item_title = item_title.split(" – ")[0]
                            description = None
                            
                        if published_date:
                            date = datetime.strptime(published_date, "%a, %d %b %Y %H:%M:%S %z")
                            date_time_jkt = date.astimezone(timezone(timedelta(hours=7)))
                            published_date = date_time_jkt.strftime("%A, %d %B %Y %H:%M:%S WIB")
                                                     
                        feed_msg = f"""
<b>Nama :</b> 
<code>{item_title if item_title else '-'}</code>

<b>Ukuran :</b> 
<code>{size if size else '-'}</code>

<b>Kategori :</b> 
<code>{category if category else '-'}</code>

<b>Deskripsi :</b> 
{description if description else '<code>-</code>'}

<b>Tanggal Dipublish :</b> 
<code>{published_date if published_date else '-'}</code>

<b>Link :</b>
<a href='{view}'>Lihat</a> {f'| <a href="{url}">Unduh</a>' if not (not_tracker or private_tracker) else ''}

#{title}{f' #{p2p_group}' if p2p_group else ''}{' #InternalRelease' if 'KQRM' in item_title else ''}
"""
                    if not_tracker:
                        reply_markup = InlineKeyboardMarkup(
                            inline_keyboard=(
                                [
                                    InlineKeyboardButton(
                                        text="👀 Lihat",
                                        url=view
                                    ),
                                ],
                            ),
                        )   
                    elif private_tracker:
                        reply_markup = InlineKeyboardMarkup(
                            inline_keyboard=(
                                [
                                    InlineKeyboardButton(
                                        text="☠️ Login",
                                        url=url
                                    ),
                                    InlineKeyboardButton(
                                        text="👀 Lihat",
                                        url=view
                                    ),
                                ],
                            ),
                        )
                    else:
                        reply_markup = InlineKeyboardMarkup(
                            inline_keyboard=(
                                [
                                    InlineKeyboardButton(
                                        text="🚀 Mirror",
                                        switch_inline_query=f"/{BotCommands.MirrorCommand[0]} {url}"
                                    ),
                                    InlineKeyboardButton(
                                        text="👀 Leech",
                                        switch_inline_query=f"/{BotCommands.LeechCommand[0]} {url}"
                                    ),
                                ],
                            ),
                        )
                    await customSendRss(feed_msg, image, image_caption, reply_markup)
                    feed_count += 1
                async with rss_dict_lock:
                    if user not in rss_dict or not rss_dict[user].get(title, False):
                        continue
                    rss_dict[user][title].update(
                        {"last_feed": last_link, "last_title": last_title}
                    )
                await DbManager().rss_update(user)
                LOGGER.info(f"Feed Name: {title}")
                LOGGER.info(f"Last item: {last_link}")
            except RssShutdownException as ex:
                LOGGER.info(ex)
                break
            except Exception as e:
                LOGGER.error(f"{e} - Feed Name: {title} - Feed Link: {data['link']}")
                continue
    if all_paused:
        scheduler.pause()


def addJob():
    scheduler.add_job(
        rssMonitor,
        trigger=IntervalTrigger(seconds=config_dict["RSS_DELAY"]),
        id="0",
        name="RSS",
        misfire_grace_time=15,
        max_instances=1,
        next_run_time=datetime.now() + timedelta(seconds=20),
        replace_existing=True,
    )


addJob()
scheduler.start()
bot.add_handler(
    MessageHandler(
        getRssMenu, filters=command(BotCommands.RssCommand) & CustomFilters.authorized
    )
)
bot.add_handler(CallbackQueryHandler(rssListener, filters=regex("^rss")))
