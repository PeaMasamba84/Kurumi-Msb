import os
import requests

from logging import (
    basicConfig,
    getLogger,
    INFO,
)
from time import sleep

basicConfig(
    format="{asctime} - [{levelname[0]}] {name} [{module}:{lineno}] - {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    level=INFO,
)

LOGGER = getLogger("alive")

def send_request(url: str) -> None:
    requests.get(
        url,
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
        },
        timeout=5
    )

try:
    PORT = os.environ.get("PORT", None)
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", "")
    RENDER_APP_NAME = os.environ.get("RENDER_APP_NAME", "")
    if len(HEROKU_APP_NAME) != 0:
        BASE_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com"
    elif len(RENDER_APP_NAME) != 0:
        BASE_URL = f"https://{RENDER_APP_NAME}.onrender.com"
    else:
        raise Exception("Auto Alive is not set up correctly! Don't forget to add HEROKU_APP_NAME or RENDER_APP_NAME to prevent the Apps got shutdown!")
        
    if (
        BASE_URL 
        and PORT is not None
    ):
        while True:
            try:
                sleep(500)
                send_request(BASE_URL)
            except:
                pass

except Exception as e:
    LOGGER.error(e)
