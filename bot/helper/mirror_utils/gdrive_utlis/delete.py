#!/usr/bin/env python3
from logging import getLogger
from googleapiclient.errors import HttpError

from bot.helper.mirror_utils.gdrive_utlis.helper import GoogleDriveHelper

LOGGER = getLogger(__name__)


class gdDelete(GoogleDriveHelper):

    def __init__(self):
        super().__init__()

    def deletefile(self, link):
        try:
            file_id = self.getIdFromUrl(link)
        except (KeyError, IndexError):
            return "<code>Google Drive ID tidak ditemukan!</code>"
        self.service = self.authorize()
        msg = ''
        try:
            self.service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
            msg = "<code>File berhasil dihapus!</code>"
            LOGGER.info(f"Delete Result: {msg}")
        except HttpError as err:
            if "File not found" in str(err) or "insufficientFilePermissions" in str(err):
                token_service = self.alt_authorize()
                if token_service is not None:
                    LOGGER.error('File not found. Trying with token.pickle...')
                    self.service = token_service
                    return self.deletefile(link)
                err = "<code>File tidak ditemukan atau tidak ada izin untuk melakukan!</code>"
            LOGGER.error(f"Delete Result: {err}")
            msg = str(err)
        return msg