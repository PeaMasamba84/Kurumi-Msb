from aiofiles.os import makedirs
from html import escape
from mega import (
    MegaApi,
    MegaError,
    MegaListener,
    MegaRequest,
    MegaTransfer,
)
from secrets import token_urlsafe
from threading import Event

from bot import (
    LOGGER,
    USE_TELEGRAPH,
    config_dict,
    non_queued_dl,
    queue_dict_lock,
    task_dict_lock,
    task_dict,
)
from bot.helper.ext_utils.bot_utils import sync_to_async
from bot.helper.ext_utils.links_utils import get_mega_link_type
from bot.helper.ext_utils.task_manager import check_running_tasks, stop_duplicate_check
from bot.helper.mirror_utils.status_utils.mega_status import MegaDownloadStatus
from bot.helper.mirror_utils.status_utils.queue_status import QueueStatus
from bot.helper.telegram_helper.message_utils import sendMessage, sendStatusMessage


class MegaAppListener(MegaListener):
    _NO_EVENT_ON = (MegaRequest.TYPE_LOGIN, MegaRequest.TYPE_FETCH_NODES)
    NO_ERROR = "no error"

    def __init__(self, continue_event: Event, listener):
        self._bytes_transferred = 0
        self._name = ""
        self._speed = 0
        self.completed = False
        self.continue_event = continue_event
        self.error = None
        self.isFile = False
        self.listener = listener
        self.node = None
        self.public_node = None
        super().__init__()

    @property
    def speed(self):
        return self._speed

    @property
    def downloaded_bytes(self):
        return self._bytes_transferred

    def onRequestFinish(self, api: MegaApi, request: MegaRequest, error):
        if self.listener.isCancelled:
            return
        if str(error).lower() != "no error":
            self.error = error.copy()
            LOGGER.error(f"Mega onRequestFinishError: {self.error}")
            self.continue_event.set()
            return
        request_type = request.getType()
        if request_type == MegaRequest.TYPE_LOGIN:
            api.fetchNodes()
        elif request_type == MegaRequest.TYPE_GET_PUBLIC_NODE:
            self.public_node = request.getPublicMegaNode()
            self._name = self.public_node.getName()
        elif request_type == MegaRequest.TYPE_FETCH_NODES:
            LOGGER.info("Fetching Root Node.")
            self.node = api.getRootNode()
            self._name = self.node.getName()
            LOGGER.info(f"Node Name: {self.node.getName()}")
        if (
            request_type not in self._NO_EVENT_ON
            or self.node
            and "cloud drive" not in self._name.lower()
        ):
            self.continue_event.set()

    def onRequestTemporaryError(self, _, __, error: MegaError):
        LOGGER.error(f"Mega Request error in {error}")
        if not self.listener.isCancelled:
            self.listener.isCancelled = True
        self.error = f"RequestTempError: {error.toString()}"
        self.continue_event.set()

    def onTransferUpdate(self, api: MegaApi, transfer: MegaTransfer):
        if self.listener.isCancelled:
            api.cancelTransfer(transfer, None)
            self.continue_event.set()
            return
        self._speed = transfer.getSpeed()
        self._bytes_transferred = transfer.getTransferredBytes()

    def onTransferFinish(self, _, transfer: MegaTransfer, __):
        try:
            if self.listener.isCancelled:
                self.continue_event.set()
            elif transfer.isFinished() and (transfer.isFolderTransfer() or self.isFile):
                self.completed = True
                self.continue_event.set()
        except Exception as e:
            LOGGER.error(e)

    def onTransferTemporaryError(self, _, transfer: MegaTransfer, error: MegaError):
        filen = transfer.getFileName()
        state = transfer.getState()
        errStr = error.toString()
        LOGGER.error(f"Mega download error in file {transfer} {filen}: {error}")
        if state in [1, 4]:
            # Sometimes MEGA (offical client) can't stream a node either and raises a temp failed error.
            # Don't break the transfer queue if transfer's in queued (1) or retrying (4) state [causes seg fault]
            return

        self.error = f"TransferTempError: {errStr} ({filen}"
        if not self.listener.isCancelled:
            self.listener.isCancelled = True
            self.continue_event.set()

    async def cancel_task(self):
        self.listener.isCancelled = True
        await self.listener.onDownloadError("Unduhan dibatalkan oleh User!")


class AsyncExecutor:
    def __init__(self):
        self.continue_event = Event()

    def do(self, function, args):
        self.continue_event.clear()
        function(*args)
        self.continue_event.wait()


async def add_mega_download(listener, path):
    MEGA_EMAIL = config_dict["MEGA_EMAIL"]
    MEGA_PASS = config_dict["MEGA_PASS"]

    executor = AsyncExecutor()
    api = MegaApi(None, None, None, "Mirror-Leech-Telegram-Bot")
    folder_api = None

    mega_listener = MegaAppListener(executor.continue_event, listener)
    api.addListener(mega_listener)

    if MEGA_EMAIL and MEGA_PASS:
        await sync_to_async(executor.do, api.login, (MEGA_EMAIL, MEGA_PASS))

    if get_mega_link_type(listener.link) == "file":
        await sync_to_async(executor.do, api.getPublicNode, (listener.link,))
        node = mega_listener.public_node
        mega_listener.isFile = True
    else:
        folder_api = MegaApi(None, None, None, "Mirror-Leech-Telegram-Bot")
        folder_api.addListener(mega_listener)
        await sync_to_async(executor.do, folder_api.loginToFolder, (listener.link,))
        node = await sync_to_async(folder_api.authorizeNode, mega_listener.node)
        
    if mega_listener.error is not None:
        await sendMessage(listener.message, str(mega_listener.error))
        await sync_to_async(executor.do, api.logout, ())
        if folder_api is not None:
            await sync_to_async(executor.do, folder_api.logout, ())
        return

    listener.name = listener.name or node.getName()
    error, button = await stop_duplicate_check(listener)
    if error:
        msg = f"<b>Hai {listener.tag} !</b>"
        msg += "\n<b>Tugasmu dihentikan karena :</b>"
        msg += f"\n<code>{escape(error)}</code>"
        
        if not USE_TELEGRAPH:
            content = [content for content in button for content in content.split("\n\n")]
            
            for _, data in enumerate(content, start=1):
                if "Hasil pencarian Google Drive" in data:
                    data = data.replace("Hasil pencarian Google Drive", "")
                    msg += data
                    
                else:
                    msg += "\n\n" + data
            
            button = None
            
            if len(msg) > 4096:
                msg = msg[:4090] + "\n..."
        await sendMessage(listener.message, msg, button)
        await sync_to_async(executor.do, api.logout, ())
        if folder_api is not None:
            await sync_to_async(executor.do, folder_api.logout, ())
        return

    gid = token_urlsafe(8)
    size = api.getSize(node)

    add_to_queue, event = await check_running_tasks(listener.mid)
    if add_to_queue:
        LOGGER.info(f"Added to Queue/Download: {listener.name}")
        async with task_dict_lock:
            task_dict[listener.mid] = QueueStatus(listener, size, gid, "Dl")
        await listener.onDownloadStart()
        if listener.multi <= 1:
            await sendStatusMessage(listener.message)
        await event.wait()
        async with task_dict_lock:
            if listener.mid not in task_dict:
                await sync_to_async(executor.do, api.logout, ())
                if folder_api is not None:
                    await sync_to_async(executor.do, folder_api.logout, ())
                return
        add_to_queue = True
        LOGGER.info(f"Start Queued Download with Mega: {listener.name}")
    else:
        add_to_queue = False

    async with task_dict_lock:
        task_dict[listener.mid] = MegaDownloadStatus(listener, mega_listener, gid, size)
    async with queue_dict_lock:
        non_queued_dl.add(listener.mid)

    if add_to_queue:
        LOGGER.info(f"Start Queued Download with Mega: {listener.name}")
    else:
        await listener.onDownloadStart()
        if listener.multi <= 1:
            await sendStatusMessage(listener.message)
        LOGGER.info(f"Download with Mega: {listener.name}")

    await makedirs(path, exist_ok=True)
    await sync_to_async(
        executor.do, api.startDownload, (node, path, listener.name, None, False, None)
    )
    await sync_to_async(executor.do, api.logout, ())
    if folder_api is not None:
        await sync_to_async(executor.do, folder_api.logout, ())

    if mega_listener.completed:
        await listener.onDownloadComplete()
    elif (error := mega_listener.error) and mega_listener.listener.isCancelled:
        await listener.onDownloadError(error)
