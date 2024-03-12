from bot.helper.ext_utils.status_utils import (
    get_readable_file_size,
    MirrorStatus,
    get_readable_time,
)


class MegaDownloadStatus:
    def __init__(self, listener, obj, gid, size):
        self.listener = listener
        self._gid = gid
        self._obj = obj
        self._size = size

    def gid(self):
        return self._gid

    def task(self):
        return self._obj

    def size(self):
        return get_readable_file_size(self._size)

    def status(self):
        return MirrorStatus.STATUS_DOWNLOADING

    def name(self):
        return self.listener.name

    def speed(self):
        return f"{get_readable_file_size(self._obj.speed)}/s"

    def eta(self):
        try:
            return get_readable_time((self._size - self._obj.downloaded_bytes) / self._obj.speed)
        except:
            return "-"

    def progress(self):
        try:
            return f"{round(self._obj.downloaded_bytes / self._size * 100, 2)}%"
        except:
            return "0.0%"
        
    def processed_bytes(self):
        return get_readable_file_size(self._obj.downloaded_bytes)