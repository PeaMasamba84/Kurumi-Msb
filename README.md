
## Setting Config File

</div>

---
<details>
    <summary><b>View All Steps<b></sup></summary>
    
```
cp config_sample.env config.env
```

- Remove the first line saying:

```
_____REMOVE_THIS_LINE_____=True
```

Fill up rest of the fields. Meaning of each field is discussed below. **NOTE**: All values must be filled between quotes, even if it's `Int`, `Bool` or `List`.

**1. Required Fields**

- `BOT_TOKEN`: The Telegram Bot Token that you got from [@BotFather](https://t.me/BotFather). `Str`
- `OWNER_ID`: The Telegram User ID (not username) of the Owner of the bot. `Int`
- `TELEGRAM_API`: This is to authenticate your Telegram account for downloading Telegram files. You can get this from <https://my.telegram.org>. `Int`
- `TELEGRAM_HASH`: This is to authenticate your Telegram account for downloading Telegram files. You can get this from <https://my.telegram.org>. `Str`

**2. Optional Fields**

- `USER_SESSION_STRING`: To download/upload from your telegram account and to send rss. To generate session string use this command `python3 generate_string_session.py` after mounting repo folder for sure. `Str`. **NOTE**: You can't use bot with private message. Use it with superGroup.
- `DATABASE_URL`: Your Mongo Database URL (Connection string). Follow this [Generate Database](#generate-database) to generate database. Data will be saved in Database: auth and sudo users, users settings including thumbnails for each user, rss data and incomplete tasks. **NOTE**: You can always edit all settings that saved in database from the official site -> (Browse collections). `Str`
- `DOWNLOAD_DIR`: The path to the local folder where the downloads should be downloaded to. `Str`
- `CMD_SUFFIX`: commands index number. This number will added at the end all commands. `Str`|`Int`
- `AUTHORIZED_CHATS`: Fill user_id and chat_id of groups/users you want to authorize. Separate them by space. `Int`
- `SUDO_USERS`: Fill user_id of users whom you want to give sudo permission. Separate them by space. `Int`
- `DEFAULT_UPLOAD`: Whether `rc` to upload to `RCLONE_PATH` or `gd` to upload to `GDRIVE_ID`. Default is `gd`. Read More [HERE](#upload).`Str`
- `STATUS_UPDATE_INTERVAL`: Time in seconds after which the progress/status message will be updated. Recommended `10` seconds at least. `Int`
- `AUTO_DELETE_MESSAGE_DURATION`: Interval of time (in seconds), after which the bot deletes it's message and command message which is expected to be viewed instantly. **NOTE**: Set to `-1` to disable auto message deletion. `Int`
- `STATUS_LIMIT`: Limit the no. of tasks shown in status message with buttons. Default is `8`. **NOTE**: Recommended limit is `4` tasks. `Int`
- `EXTENSION_FILTER`: File extensions that won't upload/clone. Separate them by space. `Str`
- `INCOMPLETE_TASK_NOTIFIER`: Get incomplete task messages after restart. Require database and superGroup. Default is `False`. `Bool`
- `UPTOBOX_TOKEN`: Uptobox token to mirror uptobox links. Get it from [Uptobox Premium Account](https://uptobox.com/my_account). `str`
- `YT_DLP_OPTIONS`: Default yt-dlp options. Check all possible options [HERE](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L184) or use this [script](https://t.me/mltb_official_channel/177) to convert cli arguments to api options. Format: key:value|key:value|key:value. Add `^` before integer or float, some numbers must be numeric and some string. `str`
  - Example: "format:bv*+mergeall[vcodec=none]|nocheckcertificate:True"
- `USE_SERVICE_ACCOUNTS`: Whether to use Service Accounts or not, with google-api-python-client. For this to work see [Using Service Accounts](#generate-service-accounts-what-is-service-account) section below. Default is `False`. `Bool`

### GDrive Tools

- `GDRIVE_ID`: This is the Folder/TeamDrive ID of the Google Drive OR `root` to which you want to upload all the mirrors using google-api-python-client. `Str`
- `IS_TEAM_DRIVE`: Set `True` if uploading to TeamDrive using google-api-python-client. Default is `False`. `Bool`
- `INDEX_URL`: Refer to <https://gitlab.com/ParveenBhadooOfficial/Google-Drive-Index>. `Str`
- `STOP_DUPLICATE`: Bot will check file/folder name in Drive incase uploading to `GDRIVE_ID`. If it's present in Drive then downloading or cloning will be stopped. (**NOTE**: Item will be checked using name and not hash, so this feature is not perfect yet). Default is `False`. `Bool`

### Rclone

- `RCLONE_PATH`: Default rclone path to which you want to upload all the files/folders using rclone. `Str`
- `RCLONE_FLAGS`: key:value|key|key|key:value . Check here all [RcloneFlags](https://rclone.org/flags/). `Str`
- `RCLONE_SERVE_URL`: Valid URL where the bot is deployed to use rclone serve. Format of URL should be `http://myip`, where `myip` is the IP/Domain(public) of your bot or if you have chosen port other than `80` so write it in this format `http://myip:port` (`http` and not `https`). `Str`
- `RCLONE_SERVE_PORT`: Which is the **RCLONE_SERVE_URL** Port. Default is `8080`. `Int`
- `RCLONE_SERVE_USER`: Username for rclone serve authentication. `Str`
- `RCLONE_SERVE_PASS`: Password for rclone serve authentication. `Str`

### Update

- `UPSTREAM_REPO`: Your github repository link, if your repo is private add `https://username:{githubtoken}@github.com/{username}/{reponame}` format. Get token from [Github settings](https://github.com/settings/tokens). So you can update your bot from filled repository on each restart. `Str`.
  - **NOTE**: Any change in docker or requirements you need to deploy/build again with updated repo to take effect. DON'T delete .gitignore file. For more information read [THIS](#upstream-repo-recommended).
- `UPSTREAM_BRANCH`: Upstream branch for update. Default is `master`. `Str`

### Leech

- `LEECH_SPLIT_SIZE`: Size of split in bytes. Default is `2GB`. Default is `4GB` if your account is premium. `Int`
- `AS_DOCUMENT`: Default type of Telegram file upload. Default is `False` mean as media. `Bool`
- `EQUAL_SPLITS`: Split files larger than **LEECH_SPLIT_SIZE** into equal parts size (Not working with zip cmd). Default is `False`. `Bool`
- `MEDIA_GROUP`: View Uploaded splitted file parts in media group. Default is `False`. `Bool`.
- `LEECH_FILENAME_PREFIX`: Add custom word to leeched file name. `Str`
- `DUMP_CHAT_ID`: Chat ID to where leeched files would be uploaded. `Int`. **NOTE**: Only available for superGroup/channel. Add `-100` before channel/superGroup id. In short don't add bot id or your id!

### qBittorrent/Aria2c

- `TORRENT_TIMEOUT`: Timeout of dead torrents downloading with qBittorrent and Aria2c in seconds. `Int`
- `BASE_URL`: Valid BASE URL where the bot is deployed to use torrent web files selection. Format of URL should be `http://myip`, where `myip` is the IP/Domain(public) of your bot or if you have chosen port other than `80` so write it in this format `http://myip:port` (`http` and not `https`). `Str`
- `BASE_URL_PORT`: Which is the **BASE_URL** Port. Default is `80`. `Int`
- `WEB_PINCODE`: Whether to ask for pincode before selecting files from torrent in web or not. Default is `False`. `Bool`.
  - **Qbittorrent NOTE**: If your facing ram issues then set limit for `MaxConnections`, decrease `AsyncIOThreadsCount`, set limit of `DiskWriteCacheSize` to `32` and decrease `MemoryWorkingSetLimit` from qbittorrent.conf or bsetting command.

### RSS

- `RSS_DELAY`: Time in seconds for rss refresh interval. Recommended `900` second at least. Default is `900` in sec. `Int`
- `RSS_CHAT_ID`: Chat ID where rss links will be sent. If you want message to be sent to the channel then add channel id. Add `-100` before channel id. `Int`
  - **RSS NOTES**: `RSS_CHAT_ID` is required, otherwise monitor will not work. You must use `USER_STRING_SESSION` --OR-- *CHANNEL*. If using channel then bot should be added in both channel and group(linked to channel) and `RSS_CHAT_ID` is the channel id, so messages sent by the bot to channel will be forwarded to group. Otherwise with `USER_STRING_SESSION` add group id for `RSS_CHAT_ID`. If `DATABASE_URL` not added you will miss the feeds while bot offline.

### MEGA

- `MEGA_EMAIL`: E-Mail used to sign-in on mega.nz for using premium account. `Str`
- `MEGA_PASSWORD`: Password for mega.nz account. `Str`

### Queue System

- `QUEUE_ALL`: Number of parallel tasks of downloads and uploads. For example if 20 task added and `QUEUE_ALL` is `8`, then the summation of uploading and downloading tasks are 8 and the rest in queue. `Int`. **NOTE**: if you want to fill `QUEUE_DOWNLOAD` or `QUEUE_UPLOAD`, then `QUEUE_ALL` value must be greater than or equal to the greatest one and less than or equal to summation of `QUEUE_UPLOAD` and `QUEUE_DOWNLOAD`.
- `QUEUE_DOWNLOAD`: Number of all parallel downloading tasks. `Int`
- `QUEUE_UPLOAD`: Number of all parallel uploading tasks. `Int`

### Torrent Search

- `SEARCH_API_LINK`: Search api app link. Get your api from deploying this [repository](https://github.com/Ryuk-me/Torrent-Api-py). `Str`
  - Supported Sites:
    > is dynamic and depend on `http://example.com/api/v1/sites` this endpoint
- `SEARCH_LIMIT`: Search limit for search api, limit for each site and not overall result limit. Default is zero (Default api limit for each site). `Int`
- `SEARCH_PLUGINS`: List of qBittorrent search plugins (github raw links). I have added some plugins, you can remove/add plugins as you want. Main Source: [qBittorrent Search Plugins (Official/Unofficial)](https://github.com/qbittorrent/search-plugins/wiki/Unofficial-search-plugins). `List`

### Limits

- `STORAGE_THRESHOLD`: To leave specific storage free and any download will lead to leave free storage less than this value will be cancelled. Don't add unit, the default unit is `GB`.
- `LEECH_LIMIT`:  To limit the Torrent/Direct/ytdlp leech size. Don't add unit, the default unit is `GB`.
- `CLONE_LIMIT`: To limit the size of Google Drive folder/file which you can clone. Don't add unit, the default unit is `GB`.
- `MEGA_LIMIT`: To limit the size of Mega download. Don't add unit, the default unit is `GB`.
- `TORRENT_LIMIT`: To limit the size of torrent download. Don't add unit, the default unit is `GB`.
- `DIRECT_LIMIT`: To limit the size of direct link download. Don't add unit, the default unit is `GB`.
- `YTDLP_LIMIT`: To limit the size of ytdlp download. Don't add unit, the default unit is `GB`.
- `GDRIVE_LIMIT`: To limit the size of Google Drive folder/file link for leech, Zip, Unzip. Don't add unit, the default unit is `GB`.

### Group Features

- `FSUB_IDS`: Fill chat_id of groups/channel you want to force subscribe. Separate them by space. `Int`
  - it will apply only for member
  - **Note**: Bot should be added in the filled chat_id as admin.
- `USER_MAX_TASKS`: Maximum number of tasks for each group member at a time. `Int`
- `REQUEST_LIMITS`: Maximum number of requests for each group member. `Int`
  - it will not accept any command/callback of user and it will mute that member for 1 minute.
- `ENABLE_MESSAGE_FILTER`: If enabled then bot will not download files with captions or forwarded. `Bool`
- `STOP_DUPLICATE_TASKS`: To enable stop duplicate task across multiple bots. `Bool`
  - **Note**: All bot must have added same database link.
- `TOKEN_TIMEOUT`: Token timeout for each group member in sec. `Int`
  - **Note**: This token system is linked with url shortners, users will have to go through ads to use bot commands (if `shorteners.txt` added, Read more about shorteners.txt [Here](https://github.com/junedkh/jmdkh-mltb#multi-shortener) ).

### Extra Features

- `SET_COMMANDS`: To set bot commands automatically on every startup. Default is `False`. `Bool`
  - **Note**: You can set commands manually according to your needs few commands are available [here](#bot-commands-to-be-set-in-botfatherhttpstmebotfather)
- `DISABLE_LEECH`: It will disable leech functionality. Default is `False`. `Bool`
- `DM_MODE`: If then bot will send Mirrored/Leeched files in user's DM. Default is `off`. `Str`
  - **Note**: if value is `mirror` it will send only mirrored files in DM. if value is `leech` so it will send leeched files in DM. if value is `all` it will send Mirrored/Leeched files in DM
- `DELETE_LINKS`: It will delete links on download start. Default is `False`. `Bool`
- `LOG_CHAT_ID`: Fill chat_id of the group/channel. It will send mirror/clone links in the log chat. `Int`
  - **Note**: Bot should be added in the log chat as admin.

    
</details></li></ol>
</details>
    
------

## Bot Commands

<details>
  <summary>Bot commands can be automatically.</kbd></sup></summary>

```
mirror - or /m Mirror
qbmirror - or /qm Mirror torrent using qBittorrent
leech - or /l Leech
qbleech - or /ql Leech torrent using qBittorrent
clone - Copy file/folder to Drive
count - Count file/folder from Drive
ytdl - or /y Mirror yt-dlp supported link
ytdlleech - or /yl Leech through yt-dlp supported link
usetting - User settings
bsetting - Bot settings
status - Get Mirror Status message
btsel - Select files from torrent
rss - Rss menu
list - Search files in Drive
search - Search for torrents with API
cancel - Cancel a task
cancelall - Cancel all tasks
del - Delete file/folder from Drive
log - Get the Bot Log
shell - Run commands in Shell
restart - Restart the Bot
stats - Bot Usage Stats
ping - Ping the Bot
help - All cmds with description
```

</details></li></ol>
</details>
    
------

## Deploy to Heroku

<details>
  <summary>Follow the instruction.</kbd></sup></summary>

```
Go to Settings, Secrets and variables, Click Actions, New repository secret.
<b>- HEROKU_EMAIL:</b> Heroku Account Email Id in which the above app will be deployed
- HEROKU_API_KEY: Your Heroku API key, get it from https://dashboard.heroku.com/account
- HEROKU_APP_NAME: Your Heroku app name, Name Must be unique
- CONFIG_FILE_URL: Copy This in any text editor.

Copy https://github.com/PeaMasamba84/Kurumi-Msb/blob/main/config_sample.env in any text editor. 
Remove the _____REMOVE_THIS_LINE_____=True line and fill the variables. 
For details about config you can see Here. Go to https://gist.github.com and paste your config data. 
Rename the file to config.env then create secret gist. Click on Raw, copy the link. 
This will be your CONFIG_FILE_URL. Refer to below images for clarity.

![Steps from 1 to 3](https://graph.org/file/2a27cf34dc0bdba885de9.jpg)

![Step 4](https://graph.org/file/fb3b92a1d2c3c1b612ad0.jpg)

![Step 5](https://graph.org/file/f0b208e4ea980b575dbe2.jpg)

3. Remove commit id from raw link to be able to change variables without updating the CONFIG_FILE_URL in secrets. Should be in this form: https://gist.githubusercontent.com/username/gist-id/raw/config.env
   - Before: https://gist.githubusercontent.com/PeaMasamba84/8cce4a4b4e7f4ea47e948b2d058e52ac/raw/19ba5ab5eb43016422193319f28bc3c7dfb60f25/config.env
   - After: https://gist.githubusercontent.com/PeaMasamba84/8cce4a4b4e7f4ea47e948b2d058e52ac/raw/config.env

4. Add all your private files in this branch.

5. In yout app settings click on reveal config vars and add CONFIG_FILE_URL
```

</details>
