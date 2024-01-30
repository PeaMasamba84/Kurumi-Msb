import os
import requests
import subprocess

from dotenv import load_dotenv, dotenv_values
from pymongo import MongoClient
from logging import (
    basicConfig,
    getLogger,
    INFO,
)

basicConfig(
    format="{asctime} - [{levelname[0]}] {name} [{module}:{lineno}] - {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    level=INFO,
)

LOGGER = getLogger("update")

if os.path.exists("log.txt"):
    with open("log.txt", "r+") as f:
        f.truncate(0)

if os.path.exists("rlog.txt"):
    os.remove("rlog.txt")

if not os.path.exists("config.env"):
    CONFIG_FILE_URL = os.environ.get("CONFIG_FILE_URL", "")
    if len(CONFIG_FILE_URL) != 0:
        LOGGER.info("CONFIG_FILE_URL is found! Downloading CONFIG_FILE_URL...")
        r = requests.get(
            CONFIG_FILE_URL
        )
        
        if not r.ok:
            LOGGER.error(f"Failed to download config.env! ERROR: [{r.status_code}] {r.text}")
    
        with open("config.env", "wb+") as file:
            file.write(r.content)
    else:
        LOGGER.warning("CONFIG_FILE_URL is not found! Using local config.env instead...")
            
load_dotenv("config.env", override=True)

if bool(os.environ.get("_____REMOVE_THIS_LINE_____")):
    LOGGER.error("The README.md file there to be read!")
    exit()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if len(BOT_TOKEN) == 0:
    LOGGER.error("BOT_TOKEN is not found!")
    exit(1)

bot_id = BOT_TOKEN.split(":", 1)[0]

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if len(DATABASE_URL) == 0:
    DATABASE_URL = None
    LOGGER.warning("DATABASE_URL is not found!")

if DATABASE_URL is not None:
    try:
        conn = MongoClient(DATABASE_URL)
        db = conn.mltb
        old_config = db.settings.deployConfig.find_one({"_id": bot_id})
        config_dict = db.settings.config.find_one({"_id": bot_id})
        if old_config is not None:
            del old_config["_id"]
        if (
            old_config is not None
            and old_config == dict(dotenv_values("config.env"))
            or old_config is None
        ) and config_dict is not None:
            os.environ["UPSTREAM_REPO"] = config_dict["UPSTREAM_REPO"]
            os.environ["UPSTREAM_BRANCH"] = config_dict["UPSTREAM_BRANCH"]
        conn.close()
    except Exception as e:
        LOGGER.error(f"DATABASE ERROR! {e}")

UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO", None)
if (
    UPSTREAM_REPO is not None
    and UPSTREAM_REPO.startswith("#")
):
    UPSTREAM_REPO = None

UPSTREAM_BRANCH = os.environ.get("UPSTREAM_BRANCH", None)
if UPSTREAM_BRANCH is None:
    UPSTREAM_BRANCH = "master"
    
if UPSTREAM_REPO is not None:
    if os.path.exists(".git"):
        subprocess.run([
            "rm -rf .git"
        ], shell=True)

    process = subprocess.run([
            f"git init -q \
            && git config --global user.email kqruumi@gmail.com \
            && git config --global user.name KQRM \
            && git add . \
            && git commit -sm update -q \
            && git remote add origin {UPSTREAM_REPO} \
            && git fetch origin -q \
            && git reset --hard origin/{UPSTREAM_BRANCH} -q"
        ], shell=True)

    if process.returncode == 0:
        LOGGER.info("Successfully updated with latest commit from UPSTREAM_REPO!")
    else:
        LOGGER.error(
            "Something wrong while updating! Check UPSTREAM_REPO if valid or not!")

else:
    LOGGER.warning("UPSTREAM_REPO is not found!")
