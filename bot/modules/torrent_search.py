from aiohttp import ClientSession
from asyncio import Lock
from html import escape
from math import ceil
from pyrogram.filters import command, regex
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from urllib.parse import quote

from bot import bot, LOGGER, USE_TELEGRAPH, config_dict, get_qb_client
from bot.helper.ext_utils.bot_utils import sync_to_async, new_task, get_telegraph_list
from bot.helper.ext_utils.status_utils import get_readable_file_size
from bot.helper.ext_utils.telegraph_helper import telegraph
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import editMessage, sendMessage


PLUGINS = []
SITES = None
MAX_LIMIT = 500
TELEGRAPH_LIMIT = 300

msg_dict = {}
max_total = 5
torrent_search_lock = Lock()


async def initiate_search_tools():
    qbclient = await sync_to_async(get_qb_client)
    qb_plugins = await sync_to_async(qbclient.search_plugins)
    if SEARCH_PLUGINS := config_dict["SEARCH_PLUGINS"]:
        globals()["PLUGINS"] = []
        src_plugins = eval(SEARCH_PLUGINS)
        if qb_plugins:
            names = [plugin["name"] for plugin in qb_plugins]
            await sync_to_async(qbclient.search_uninstall_plugin, names=names)
        await sync_to_async(qbclient.search_install_plugin, src_plugins)
    elif qb_plugins:
        for plugin in qb_plugins:
            await sync_to_async(qbclient.search_uninstall_plugin, names=plugin["name"])
        globals()["PLUGINS"] = []
    await sync_to_async(qbclient.auth_log_out)

    if SEARCH_API_LINK := config_dict["SEARCH_API_LINK"]:
        global SITES
        try:
            async with ClientSession() as c:
                async with c.get(f"{SEARCH_API_LINK}/api/v1/sites") as res:
                    data = await res.json()
            SITES = {
                str(site): str(site).capitalize() for site in data["supported_sites"]
            }
            SITES["all"] = "All"
        except Exception as e:
            LOGGER.error(
                f"{e} Can't fetching sites from SEARCH_API_LINK make sure use latest version of API"
            )
            SITES = None


async def _search(key, site, message, method):
    if method.startswith("api"):
        SEARCH_API_LINK = config_dict["SEARCH_API_LINK"]
        SEARCH_LIMIT = config_dict["SEARCH_LIMIT"]
        if method == "apisearch":
            LOGGER.info(f"Searching (Api) : {key} from {site}")
            if site == "all":
                api = f"{SEARCH_API_LINK}/api/v1/all/search?query={key}&limit={SEARCH_LIMIT}"
            else:
                api = f"{SEARCH_API_LINK}/api/v1/search?site={site}&query={key}&limit={SEARCH_LIMIT}"
        elif method == "apitrend":
            LOGGER.info(f"Api Trending from {site}")
            if site == "all":
                api = f"{SEARCH_API_LINK}/api/v1/all/trending?limit={SEARCH_LIMIT}"
            else:
                api = f"{SEARCH_API_LINK}/api/v1/trending?site={site}&limit={SEARCH_LIMIT}"
        elif method == "apirecent":
            LOGGER.info(f"Api Recent from {site}")
            if site == "all":
                api = f"{SEARCH_API_LINK}/api/v1/all/recent?limit={SEARCH_LIMIT}"
            else:
                api = (
                    f"{SEARCH_API_LINK}/api/v1/recent?site={site}&limit={SEARCH_LIMIT}"
                )
        try:
            async with ClientSession() as c:
                async with c.get(api) as res:
                    search_results = await res.json()
            if "error" in search_results or search_results["total"] == 0:
                await editMessage(
                    message,
                    f"<b>Pencarian tidak ditemukan!</b>\n╾────────────╼\n<b>Situs :</b> <code>{SITES.get(site)}</code>\n<b>Kata Kunci :</b> <code>{key.title()}</code>\n╾────────────╼\n",
                )
                return
            msg = f"<b>Menemukan</b> <code>{min(search_results['total'], MAX_LIMIT)}</code> <b>hasil pencarian!</b>"
            msg += "\n╾────────────╼\n"
            msg += f"<b>Situs :</b> <code>{SITES.get(site)}</code>"
            if method == "apitrend":
                msg += f"\n<b>Metode :</b> <code>Api Trending</code>"
            elif method == "apirecent":
                msg += f"\n<b>Metode :</b> <code>Api Trending</code>"
            else:
                msg += f"\n<b>Metode :</b> <code>Api Search</code>"
                msg += f"\n<b>Kata Kunci :</b> <code>{key.title()}</code>"
            msg += "\n╾────────────╼\n"
            search_results = search_results["data"]
        except Exception as e:
            await editMessage(message, str(e))
            return
    else:
        LOGGER.info(f"Searching (Plugins) : {key} from {site}")
        client = await sync_to_async(get_qb_client)
        search = await sync_to_async(
            client.search_start, pattern=key, plugins=site, category="all"
        )
        search_id = search.id
        while True:
            result_status = await sync_to_async(
                client.search_status, search_id=search_id
            )
            status = result_status[0].status
            if status != "Running":
                break
        dict_search_results = await sync_to_async(
            client.search_results, search_id=search_id, limit=MAX_LIMIT
        )
        search_results = dict_search_results.results
        total_results = dict_search_results.total
        if total_results == 0:
            await editMessage(
                message,
                f"<b>Pencarian tidak ditemukan!</b>\n╾────────────╼\n<b>Situs :</b> <code>{site.capitalize()}</code>\n<b>Metode :</b> <code>Plugins Search</code>\n<b>Kata Kunci :</b> <code>{key.title()}</code>\n╾────────────╼\n",
            )
            return
        msg = f"<b>Menemukan</b> <code>{min(total_results, MAX_LIMIT)}</code> <b>hasil pencarian!</b>\n╾────────────╼\n<b>Situs :</b>{site.capitalize()}\n<b>Metode :</b> <code>Plugins Search</code>\n<b>Kata Kunci :</b> <code>{key.title()}</code>\n╾────────────╼\n"
        await sync_to_async(client.search_delete, search_id=search_id)
        await sync_to_async(client.auth_log_out)
    
    content = await _getResult(search_results, key, method)
    
    if USE_TELEGRAPH:
        try:
            button = await get_telegraph_list(content)
        except Exception as e:
            await editMessage(message, e)
            return
        
        await editMessage(message, msg, button)
    
    else:
        msg = ""
        button = None
        
        page = 0
        page_no = 1 
        page_cur = None
        
        pages = [content for content in content for content in content.split("\n\n")]
        
        msgId = message.reply_to_message.id
        userId = message.reply_to_message.from_user.id 
        
        msg_dict[msgId] = [page, pages, page_no, page_cur, key, msgId]
        
        async with torrent_search_lock:
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
                buttons.ibutton("⏪", f"tg_search {userId} pre {msgId}")
                buttons.ibutton(f"{page_no}/{page_cur}", f"tg_search {userId} ref {msgId}")
                buttons.ibutton("⏩", f"tg_search {userId} nex {msgId}")

            if len(pages) <= max_total:
                buttons.ibutton(f"{page_no}/{page_cur}", f"tg_search {userId} ref {msgId}")

        buttons.ibutton("Close", f"tg_search {userId} close {msgId}", position="footer")
        await editMessage(message, msg, buttons.build_menu(3))


async def _getResult(search_results, key, method):
    msg = ""
    content = []
    
    Torrent = False

    if USE_TELEGRAPH:
        msg += f"<h4>Hasil pencarian Torrent</h4>"
    else:
        msg += f"<b>Hasil pencarian Torrent</b>"

    msg += "\n╾────────────╼\n"
    
    if method == "apirecent":
        msg += "<b>Metode :</b> <code>Api Recent</code>"
        
    elif method == "apisearch":
        msg += "<b>Metode :</b> <code>Api Search</code>"
        if USE_TELEGRAPH:
            msg += "<br>"
        else:
            msg += "\n"
        msg += f"<b>Kata Kunci :</b> <code>{key.title()}</code>"
        
    elif method == "apitrend":
        msg += "<b>Metode :</b> <code>Api Trending</code>"
        
    else:
        msg += "<b>Metode :</b> <code>Plugins Search</code>"
        if USE_TELEGRAPH:
            msg += "<br>"
        else:
            msg += "\n"
        msg += f"<b>Kata Kunci :</b> <code>{key.title()}</code>"
        
    msg += "\n╾────────────╼\n"
        
    for index, result in enumerate(search_results, start=1):
        if method.startswith("api"):
            try:
                if "name" in result.keys():
                    msg += f"<code><a href='{result['url']}'>{escape(result['name'])}</a></code>"
                    
                    if USE_TELEGRAPH:
                        msg += "<br>"
                    else:
                        msg += "\n"
                        
                if "torrents" in result.keys():
                    for subres in result["torrents"]:
                        msg += f"<b>Type :</b> <code>{subres['type']}</code>"
                        msg += f"<b> | Size :</b> <code>{subres['size']}</code>"
                        msg += f"<b> | Quality :</b> <code>{subres['quality']}</code>"

                        if USE_TELEGRAPH:
                            msg += "<br>"
                        else:
                            msg += "\n"
                            
                        if "torrent" in subres.keys():
                            Torrent = True
                            msg += f"<a href='{subres['torrent']}'>🦠 Unduh</a>"
                            msg += f"<b> | <a href='{subres['torrent']}'>⚡ Direct</a></b>"
                            
                        if "magnet" in subres.keys():
                            if Torrent:
                                msg += f"<b> | <a href='http://t.me/share/url?url={subres['magnet']}'>🧲 Magnet</a></b>"
                            else:
                                msg += f"<b><a href='http://t.me/share/url?url={subres['magnet']}'>🧲 Magnet</a></b>"
                    
                else:
                    msg += f"<b>Size :</b> <code>{result['size']}</code>"

                    if USE_TELEGRAPH:
                        msg += "<br>"
                    else:
                        msg += "\n"
                        
                    try:
                        msg += f"<b>Seeders :</b> <code>{result['seeders']}</code>"
                        msg += f"<b> | Leechers :</b> <code>{result['leechers']}</code>"
                        if USE_TELEGRAPH:
                            msg += "<br>"
                        else:
                            msg += "\n"
                    except:
                        pass
                    
                    if "torrent" in result.keys():
                        Torrent = True
                        msg += f"<b><a href='{result['torrent']}'>🦠 Unduh</a></b>"
                        msg += f"<b> | <a href='{result['torrent']}'>⚡ Direct</a></b>"
                        
                    elif "magnet" in result.keys():
                        if Torrent:
                            msg += f"<b> | <a href='http://t.me/share/url?url={result['magnet']}'>🧲 Magnet</a></b>"
                        else:
                            msg += f"<b><a href='http://t.me/share/url?url={result['magnet']}'>🧲 Magnet</a></b>"
                            
                    else:
                        if USE_TELEGRAPH:
                            msg += "<br>"
                        else:
                            msg += "\n"
                        
            except:
                continue
            
        else:
            msg += f"<code><a href='{result.descrLink}'>{escape(result.fileName)}</a></code>"
            if USE_TELEGRAPH:
                msg += "<br>"
            else:
                msg += "\n"
                
            msg += f"<b>Size :</b> <code>{get_readable_file_size(result.fileSize)}</code>"
            if USE_TELEGRAPH:
                msg += "<br>"
            else:
                msg += "\n"
                
            msg += f"<b>Seeders :</b> <code>{result.nbSeeders}</code>"
            msg += f"<b> | Leechers :</b> <code>{result.nbLeechers}</code>"
            if USE_TELEGRAPH:
                msg += "<br>"
            else:
                msg += "\n"
                
            link = result.fileUrl
            
            if link.startswith("magnet:"):
                msg += f"<b><a href='http://t.me/share/url?url={link}'>🧲 Magnet</a></b>"
            else:
                msg += f"<b><a href='{link}'>🦠 Unduh</a></b>"
                msg += f"<b> | <a href='{link}'>⚡ Direct</a></b>"

        if USE_TELEGRAPH:
            msg += "<br><br>"
        else:
            msg += "\n\n"

        if len(msg.encode("utf-8")) > 39000:
            content.append(msg)
            msg = ""

        if (
            USE_TELEGRAPH
            and index == TELEGRAPH_LIMIT
        ):
            break

    if msg != "":
        content.append(msg)
    
    return content


def _api_buttons(user_id, method):
    buttons = ButtonMaker()
    for data, name in SITES.items():
        buttons.ibutton(name, f"torser {user_id} {data} {method}")
    buttons.ibutton("Cancel", f"torser {user_id} cancel")
    return buttons.build_menu(2)


async def _plugin_buttons(user_id):
    buttons = ButtonMaker()
    if not PLUGINS:
        qbclient = await sync_to_async(get_qb_client)
        pl = await sync_to_async(qbclient.search_plugins)
        for name in pl:
            PLUGINS.append(name["name"])
        await sync_to_async(qbclient.auth_log_out)
    for siteName in PLUGINS:
        buttons.ibutton(siteName.capitalize(), f"torser {user_id} {siteName} plugin")
    buttons.ibutton("All", f"torser {user_id} all plugin")
    buttons.ibutton("Cancel", f"torser {user_id} cancel")
    return buttons.build_menu(2)


async def torrentSearch(_, message):
    user_id = message.from_user.id
    buttons = ButtonMaker()
    key = message.text.split()
    SEARCH_PLUGINS = config_dict["SEARCH_PLUGINS"]
    if SITES is None and not SEARCH_PLUGINS:
        await sendMessage(
            message, "<b>Api atau Plugin tidak tersedia!</b>"
        )
    elif len(key) == 1 and SITES is None:
        await sendMessage(message, "<b>Kirim perintah disertai dengan Kata Kunci!</b>")
    elif len(key) == 1:
        buttons.ibutton("Trending", f"torser {user_id} apitrend")
        buttons.ibutton("Recent", f"torser {user_id} apirecent")
        buttons.ibutton("Cancel", f"torser {user_id} cancel")
        button = buttons.build_menu(2)
        await sendMessage(message, "<b>Kirim perintah disertai dengan Kata Kunci!</b>", button)
    elif SITES is not None and SEARCH_PLUGINS:
        buttons.ibutton("Api", f"torser {user_id} apisearch")
        buttons.ibutton("Plugins", f"torser {user_id} plugin")
        buttons.ibutton("Cancel", f"torser {user_id} cancel")
        button = buttons.build_menu(2)
        await sendMessage(message, "<b>Pilih Alat untuk mencari :</b>", button)
    elif SITES is not None:
        button = _api_buttons(user_id, "apisearch")
        await sendMessage(message, "<b>Pilih Situs untuk dicari | Api :</b>", button)
    else:
        button = await _plugin_buttons(user_id)
        await sendMessage(message, "<b>Pilih Situs untuk dicari | Plugins :</b>", button)


@new_task
async def torrentSearchUpdate(_, query):
    user_id = query.from_user.id
    message = query.message
    key = message.reply_to_message.text.split(maxsplit=1)
    key = key[1].strip() if len(key) > 1 else None
    data = query.data.split()
    if user_id != int(data[1]):
        await query.answer("Bukan Tugas darimu!", show_alert=True)
    elif data[2].startswith("api"):
        await query.answer()
        button = _api_buttons(user_id, data[2])
        await editMessage(message, "<b>Pilih situs :</b>", button)
    elif data[2] == "plugin":
        await query.answer()
        button = await _plugin_buttons(user_id)
        await editMessage(message, "<b>Pilih situs :</b>", button)
    elif data[2] != "cancel":
        await query.answer()
        site = data[2]
        method = data[3]
        msg = "<b>Mencari Torrent...</b>"
        msg += "\n╾────────────╼\n"
        if method.startswith("api"):
            msg += f"<b>Situs :</b> <code>{SITES.get(site)}</code>"
            if key is None:
                if method == "apirecent":
                    endpoint = "Api Recent"
                elif method == "apitrend":
                    endpoint = "Api Trending"
                msg += f"\n<b>Metode :</b> <code>{endpoint}</code>"
                msg += "\n╾────────────╼\n"
                await editMessage(
                    message,
                    msg,
                )
            else:
                msg += f"<b>Situs :</b> <code>{SITES.get(site)}</code>"
                msg += f"\n<b>Metode :</b> <code>Api Search</code>"
                msg += f"\n<b>Kata Kunci :</b> <code>{key.title()}</code>"
                msg += "\n╾────────────╼\n"
                await editMessage(
                    message,
                    f"<b>Situs :</b> <code>{SITES.get(site)}</code>\n\n╾────────────╼\n",
                )
        else:
            msg += f"<b>Situs :</b> <code>{site.capitalize()}</code>"
            msg += f"\n<b>Metode :</b> <code>Plugins Search</code>"
            msg += f"\n<b>Kata Kunci :</b> <code>{key.title()}</code>"
            msg += "\n╾────────────╼\n"
            await editMessage(
                message,
                msg,
            )
        await _search(key, site, message, method)
    else:
        await query.answer()
        await editMessage(message, "<b>Pencarian dibatalkan!</b>")


@new_task
async def telegram_search(_, query):
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
            buttons.ibutton("⏪", f"tg_search {userId} pre {msgs[5]}")
            buttons.ibutton(f"{msgs[2]}/{page_cur}", f"tg_search {userId} ref {msgs[5]}")
            buttons.ibutton("⏩", f"tg_search {userId} nex {msgs[5]}")
            
        if len(msgs[1]) <= max_total:
            buttons.ibutton(f"{msgs[2]}/{page_cur}", f"tg_search {userId} ref {msgs[5]}")
            
        buttons.ibutton("Close", f"tg_search {userId} close {msgs[5]}", position="footer")
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
            buttons.ibutton("⏪", f"tg_search {userId} pre {msgs[5]}")
            buttons.ibutton(f"{msgs[2]}/{page_cur}", f"tg_search {userId} ref {msgs[5]}")
            buttons.ibutton("⏩", f"tg_search {userId} nex {msgs[5]}")
            
        if len(msgs[1]) <= max_total:
            buttons.ibutton(f"{msgs[2]}/{page_cur}", f"tg_search {userId} ref {msgs[5]}")
        
        buttons.ibutton("Close", f"tg_search {userId} close {msgs[5]}", position="footer")
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
        torrentSearch,
        filters=command(
            BotCommands.SearchCommand
        ) & CustomFilters.authorized,
    )
)
bot.add_handler(
    CallbackQueryHandler(
        torrentSearchUpdate, 
        filters=regex(
            "^torser"
        )
    )
)
bot.add_handler(
    CallbackQueryHandler(
        telegram_search, 
        filters=regex(
            "^tg_search")
    )
)