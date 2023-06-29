from os import environ
from time import sleep
from logging import getLogger, error as log_error, warning as log_warning
from requests import get as rget

LOGGER = getLogger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10"}

try:
    HEROKU_APP_NAME = environ.get("HEROKU_APP_NAME", "")
    RENDER_APP_NAME = environ.get("RENDER_APP_NAME", "")
    PORT = environ.get("PORT")
    if not len(HEROKU_APP_NAME) == 0:
        BASE_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com"
        if BASE_URL and len(PORT) != 0:
            while True:
                try:
                    sleep(500)
                    rget(BASE_URL, headers=headers, timeout=5)
                except:
                    pass
    elif not len(RENDER_APP_NAME) == 0:
        BASE_URL = f"https://{RENDER_APP_NAME}.onrender.com"
        if BASE_URL and len(PORT) != 0:
            while True:
                try:
                    sleep(500)
                    rget(BASE_URL, headers=headers, timeout=5)
                except:
                    pass
    else:
        log_warning("Failed to Set Up Auto Alive")
except Exception as e:
    log_error(e)
