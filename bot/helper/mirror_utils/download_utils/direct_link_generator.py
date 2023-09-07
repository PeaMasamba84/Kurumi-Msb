# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Helper Module containing various sites direct links generators. This module is copied and modified as per need
from https://github.com/AvinashReddy3108/PaperplaneExtended . I hereby take no credit of the following code other
than the modifications. See https://github.com/AvinashReddy3108/PaperplaneExtended/commits/master/userbot/modules/direct_links.py
for original authorship. """
import json
import requests

from base64 import b64decode
from bs4 import BeautifulSoup
from cloudscraper import create_scraper
from hashlib import sha256
from http.cookiejar import MozillaCookieJar
from json import loads
from lk21 import Bypass
from lxml.etree import HTML
from os import path
from re import findall, match, search, sub
from requests.adapters import HTTPAdapter
from threading import Thread
from time import sleep
from urllib.parse import parse_qs, quote, unquote, urlparse
from urllib3.util.retry import Retry
from uuid import uuid4

from bot import config_dict
from bot.helper.ext_utils.bot_utils import get_readable_time, is_share_link, text_size_to_bytes
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.ext_utils.help_messages import PASSWORD_ERROR_MESSAGE

_caches = {}

fmed_list = ['fembed.net', 'fembed.com', 'femax20.com', 'fcdn.stream', 'feurl.com', 'layarkacaxxi.icu',
             'naniplay.nanime.in', 'naniplay.nanime.biz', 'naniplay.com', 'mm9842.com']

anonfilesBaseSites = ['anonfiles.com', 'hotfile.io', 'bayfiles.com', 'megaupload.nz', 'letsupload.cc',
                      'filechan.org', 'myfile.is', 'vshare.is', 'rapidshare.nu', 'lolabits.se',
                      'openload.cc', 'share-online.is', 'upvid.cc', 'zippysha.re']

pake_sites = ['dood.watch', 'doodstream.com', 'dood.to', 'dood.so', 'dood.cx', 'dood.la', 'dood.ws', 'dood.sh', 'doodstream.co', 'dood.pm', 'dood.wf', 'dood.re', 'dood.video', 'dooood.com', 'dood.yt', 'dood.stream', 'doods.pro']


def direct_link_generator(link: str):
    """ direct links generator """
    domain = urlparse(link).hostname
    if not domain:
        raise DirectDownloadLinkException("ERROR: URL Salah!")
    if 'youtube.com' in domain or 'youtu.be' in domain:
        raise DirectDownloadLinkException(
            "ERROR: Gunakan perintah ytdl untuk mengunduh Youtube!")
    elif 'yadi.sk' in domain or 'disk.yandex.com' in domain:
        return yandex_disk(link)
    elif 'mediafire.com' in domain:
        return mediafire(link)
    elif 'uptobox.com' in domain:
        return uptobox(link)
    elif 'osdn.net' in domain:
        return osdn(link)
    elif 'github.com' in domain:
        return github(link)
    elif 'hxfile.co' in domain:
        return hxfile(link)
    elif '1drv.ms' in domain:
        return onedrive(link)
    elif 'pixeldrain.com' in domain:
        return pixeldrain(link)
    elif 'antfiles.com' in domain:
        return antfiles(link)
    elif 'racaty' in domain:
        return racaty(link)
    elif '1fichier.com' in domain:
        return fichier(link)
    elif 'solidfiles.com' in domain:
        return solidfiles(link)
    elif 'krakenfiles.com' in domain:
        return krakenfiles(link)
    elif 'upload.ee' in domain:
        return uploadee(link)
    elif 'akmfiles' in domain:
        return akmfiles(link)
    elif 'linkbox' in domain or 'ibx.to' in domain:
        return linkbox(link)
    elif 'shrdsk' in domain:
        return shrdsk(link)
    elif 'letsupload.io' in domain:
        return letsupload(link)
    elif 'gofile.io' in domain:
        return gofile(link)
    elif 'send.cm' in domain:
        return send_cm(link)
    elif 'easyupload.io' in domain:
        return easyupload(link)
    # elif 'doods.pro' in domain:
    #     return doods(link)
    elif any(x in domain for x in pake_sites):
        return pake(link)
    elif any(x in domain for x in ['streamtape.com', 'streamtape.co', 'streamtape.cc', 'streamtape.to', 'streamtape.net', 'streamta.pe', 'streamtape.xyz', 'tapewithadblock.org']):
        return streamtape(link)
    elif any(x in domain for x in ['wetransfer.com', 'we.tl']):
        return wetransfer(link)
    elif any(x in domain for x in anonfilesBaseSites):
        return anonfilesBased(link)
    elif any(x in domain for x in ['terabox.com', 'nephobox.com', '4funbox.com', 'mirrobox.com', 'momerybox.com', 'teraboxapp.com', '1024tera.com']):
        return terabox(link)
    elif any(x in domain for x in fmed_list):
        return fembed(link)
    elif any(x in domain for x in ['sbembed.com', 'watchsb.com', 'streamsb.net', 'sbplay.org']):
        return sbembed(link)
    elif is_share_link(link):
        if 'gdtot' in domain:
            return gdtot(link)
        elif 'filepress' in domain:
            return filepress(link)
        else:
            return sharer_scraper(link)
    elif 'zippyshare.com' in domain:
        raise DirectDownloadLinkException('ERROR: R.I.P Zippyshare')
    elif 'mp4upload.com' in domain:
        return mp4upload(link)
    elif 'androiddatahost.com' in domain:
        return androiddatahost(link)
    elif "apkadmin.com" in domain or "sharemods.com" in domain:
        return apkadmin(link)
    elif 'sourceforge' in domain:
        return sourceforge(link)
    elif 'androidfilehost.com' in link:
        return androidfilehost(link)
    elif 'tusfiles.net' in domain or 'tusfiles.com' in domain:
        return tusfiles(link)
    elif 'pandafiles.com' in domain:
        return pandafiles(link)
    elif 'uploadhaven.com' in domain:
        return uploadhaven(link)
    elif "uploadrar.com" in domain:
        return uploadrar(link)
    elif "romsget.io" in domain:
        return link if domain == "static.romsget.io" else romsget(link)
    elif "hexupload.net" in domain:
        return hexupload(link)
    else:
        raise DirectDownloadLinkException(
            f'Tidak ada fungsi Generator Direct Link untuk {link}')


def get_captcha_token(session, params):
    recaptcha_api = 'https://www.google.com/recaptcha/api2'
    res = session.get(f'{recaptcha_api}/anchor', params=params)
    anchor_html = HTML(res.text)
    if not (anchor_token:= anchor_html.xpath('//input[@id="recaptcha-token"]/@value')):
        return
    params['c'] = anchor_token[0]
    params['reason'] = 'q'
    res = session.post(f'{recaptcha_api}/reload', params=params)
    if token := findall(r'"rresp","(.*?)"', res.text):
        return token[0]


def yandex_disk(url: str) -> str:
    """ Yandex.Disk direct link generator
    Based on https://github.com/wldhx/yadisk-direct """
    try:
        link = findall(r'\b(https?://(yadi.sk|disk.yandex.com)\S+)', url)[0][0]
    except IndexError:
        return "Link Yandex.Disk tidak ditemukan!\n"
    api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    cget = create_scraper().request
    try:
        return cget('get', api.format(link)).json()['href']
    except KeyError:
        raise DirectDownloadLinkException(
            "ERROR: Link File tidak ditemukan!")


def uptobox(url: str) -> str:
    """ Uptobox direct link generator
    based on https://github.com/jovanzers/WinTenCermin and https://github.com/sinoobie/noobie-mirror """
    try:
        urls = findall(r'\bhttps?://.*uptobox\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("ERROR: Link Uptobox tidak ditemukan!")
    if urls := findall(r'\bhttps?://.*\.uptobox\.com/dl\S+', url):
        return urls[0]
    if "::" in url:
        _password = url.split("::")[-1]
    else:
        _password = None
    cget = create_scraper().request
    try:
        file_id = findall(r'\bhttps?://.*uptobox\.com/(\w+)', url)[0]
        if UPTOBOX_TOKEN := config_dict['UPTOBOX_TOKEN']:
            file_link = f'https://uptobox.com/api/link?token={UPTOBOX_TOKEN}&file_code={file_id}'
        else:
            file_link = f'https://uptobox.com/api/link?file_code={file_id}'
        if _password:
            file_link = file_link + f'&password={_password}'
        res = cget('get', file_link).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    if res['statusCode'] == 0:
        return res['data']['dlLink']
    elif res['statusCode'] == 16:
        sleep(1)
        waiting_token = res["data"]["waitingToken"]
        sleep(res["data"]["waiting"])
    elif res['statusCode'] == 17:
        raise DirectDownloadLinkException(f"ERROR:\n{PASSWORD_ERROR_MESSAGE.format(url)}")
    elif res['statusCode'] == 39:
        raise DirectDownloadLinkException(
            f"ERROR: Uptobox sedang limit! Silahkan tunggu {get_readable_time(res['data']['waiting'])} lagi!")
    else:
        raise DirectDownloadLinkException(f"ERROR: {res['message']}")
    try:
        res = cget('get', f"{file_link}&waitingToken={waiting_token}").json()
        return res['data']['dlLink']
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")


def mediafire(url: str) -> str:
    if '/folder/' in url:
        return mediafireFolder(url)
    if final_link := findall(r'https?:\/\/download\d+\.mediafire\.com\/\S+\/\S+\/\S+', url):
        return final_link[0]
    try:
        with requests.Session() as scraper:
            page = scraper.get(url).text
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    if not (final_link := findall(r"\'(https?:\/\/download\d+\.mediafire\.com\/\S+\/\S+\/\S+)\'", page)):
        try:
            page = BeautifulSoup(page, 'lxml')
            final_link = [
                page.find('a', {'aria-label': 'Download file'}).get('href')]
        except:
            raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")
    return final_link[0]


def mediafireFolder(url: str):
    try:
        raw = url.split('/', 4)[-1]
        folderkey = raw.split('/', 1)[0]
        folderkey = folderkey.split(',')
    except:
        raise DirectDownloadLinkException('ERROR: Link Folder tidak ditemukan!')
    if len(folderkey) == 1:
        folderkey = folderkey[0]
    details = {'contents': [], 'title': '', 'total_size': 0, 'header': ''}
    
    session = requests.session()
    adapter = HTTPAdapter(max_retries=Retry(
        total=10, read=10, connect=10, backoff_factor=0.3))
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session = create_scraper(
        browser={"browser": "firefox", "platform": "windows", "mobile": False},
        delay=10,
        sess=session,
    )
    folder_infos = []

    def __get_info(folderkey):
        try:
            if isinstance(folderkey, list):
                folderkey = ','.join(folderkey)
            _json = session.post('https://www.mediafire.com/api/1.5/folder/get_info.php', data={
                'recursive': 'yes',
                'folder_key': folderkey,
                'response_format': 'json'
            }).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__} ketika mencoba mendapatkan Info Folder!")
        _res = _json['response']
        if 'folder_infos' in _res:
            folder_infos.extend(_res['folder_infos'])
        elif 'folder_info' in _res:
            folder_infos.append(_res['folder_info'])
        elif 'message' in _res:
            raise DirectDownloadLinkException(f"ERROR: {_res['message']}")
        else:
            raise DirectDownloadLinkException("ERROR: Info Folder tidak ditemukan!")


    try:
        __get_info(folderkey)
    except Exception as e:
        raise DirectDownloadLinkException(e)

    details['title'] = folder_infos[0]["name"]

    def __scraper(url):
        try:
            html = HTML(session.get(url).text)
        except:
            return
        if final_link := html.xpath("//a[@id='downloadButton']/@href"):
            return final_link[0]

    def __get_content(folderKey, folderPath='', content_type='folders'):
        try:
            params = {
                'content_type': content_type,
                'folder_key': folderKey,
                'response_format': 'json',
            }
            _json = session.get('https://www.mediafire.com/api/1.5/folder/get_content.php', params=params).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__} ketika mencoba mendapatkan Info File!")
        _res = _json['response']
        if 'message' in _res:
            raise DirectDownloadLinkException(f"ERROR: {_res['message']}")
        _folder_content = _res['folder_content']
        if content_type == 'folders':
            folders = _folder_content['folders']
            for folder in folders:
                if folderPath:
                    newFolderPath = path.join(folderPath, folder["name"])
                else:
                    newFolderPath = path.join(folder["name"])
                __get_content(folder['folderkey'], newFolderPath)
            __get_content(folderKey, folderPath, 'files')
        else:
            files = _folder_content['files']
            for file in files:
                item = {}
                if not (_url := __scraper(file['links']['normal_download'])):
                    continue
                item['filename'] = file["filename"]
                if not folderPath:
                    folderPath = details['title']
                item['path'] = path.join(folderPath)
                item['url'] = _url
                if 'size' in file:
                    size = file["size"]
                    if isinstance(size, str) and size.isdigit():
                        size = float(size)
                    details['total_size'] += size
                details['contents'].append(item)
    try:
        threads = []
        for folder in folder_infos:
            thread = Thread(target=__get_content, args=(folder['folderkey'], folder['name']))
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(e)
    session.close()
    return details


def osdn(url: str) -> str:
    """ OSDN direct link generator """
    osdn_link = 'https://osdn.net'
    try:
        link = findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("Link OSDN tidak ditemukan!")
    cget = create_scraper().request
    try:
        page = BeautifulSoup(
            cget('get', link, allow_redirects=True).content, 'lxml')
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    info = page.find('a', {'class': 'mirror_link'})
    link = unquote(osdn_link + info['href'])
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    urls = []
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        urls.append(sub(r'm=(.*)&f', f'm={mirror}&f', link))
    return urls[0]


def github(url: str) -> str:
    """ GitHub direct links generator """
    try:
        findall(r'\bhttps?://.*github\.com.*releases\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("Link Github Release tidak ditemukan!")
    cget = create_scraper().request
    download = cget('get', url, stream=True, allow_redirects=False)
    try:
        return download.headers["location"]
    except KeyError:
        raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")


def hxfile(url: str) -> str:
    """ Hxfile direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        return Bypass().bypass_filesIm(url)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")


def letsupload(url: str) -> str:
    cget = create_scraper().request
    try:
        res = cget("POST", url)
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if direct_link := findall(r"(https?://letsupload\.io\/.+?)\'", res.text):
        return direct_link[0]
    else:
        raise DirectDownloadLinkException('ERROR: Link File tidak ditemukan!')


def anonfilesBased(url: str) -> str:
    cget = create_scraper().request
    try:
        soup = BeautifulSoup(cget('get', url).content, 'lxml')
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    if sa := soup.find(id="download-url"):
        return sa['href']
    raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")


def fembed(link: str) -> str:
    """ Fembed direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        dl_url = Bypass().bypass_fembed(link)
        count = len(dl_url)
        lst_link = [dl_url[i] for i in dl_url]
        return lst_link[count-1]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")


def sbembed(link: str) -> str:
    """ Sbembed direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        dl_url = Bypass().bypass_sbembed(link)
        count = len(dl_url)
        lst_link = [dl_url[i] for i in dl_url]
        return lst_link[count-1]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")


def onedrive(link: str) -> str:
    cget = create_scraper().request
    try:
        link = cget('get', link).url
        parsed_link = urlparse(link)
        link_data = parse_qs(parsed_link.query)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    if not link_data:
        raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")
    folder_id = link_data.get('resid')
    if not folder_id:
        raise DirectDownloadLinkException('ERROR: Folder ID tidak ditemukan!')
    folder_id = folder_id[0]
    authkey = link_data.get('authkey')
    if not authkey:
        raise DirectDownloadLinkException('ERROR: Authkey tidak ditemukan!')
    authkey = authkey[0]
    boundary = uuid4()
    headers = {'content-type': f'multipart/form-data;boundary={boundary}'}
    data = f'--{boundary}\r\nContent-Disposition: form-data;name=data\r\nPrefer: Migration=EnableRedirect;FailOnMigratedFiles\r\nX-HTTP-Method-Override: GET\r\nContent-Type: application/json\r\n\r\n--{boundary}--'
    try:
        resp = cget(
            'get', f'https://api.onedrive.com/v1.0/drives/{folder_id.split("!", 1)[0]}/items/{folder_id}?$select=id,@content.downloadUrl&ump=1&authKey={authkey}', headers=headers, data=data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if "@content.downloadUrl" not in resp:
        raise DirectDownloadLinkException('ERROR: Link File tidak ditemukan!')
    return resp['@content.downloadUrl']


def pixeldrain(url: str) -> str:
    """ Based on https://github.com/yash-dk/TorToolkit-Telegram """
    url = url.strip("/ ")
    file_id = url.split("/")[-1]
    if url.split("/")[-2] == "l":
        info_link = f"https://pixeldrain.com/api/list/{file_id}"
        dl_link = f"https://pixeldrain.com/api/list/{file_id}/zip?download"
    else:
        info_link = f"https://pixeldrain.com/api/file/{file_id}/info"
        dl_link = f"https://pixeldrain.com/api/file/{file_id}?download"
    cget = create_scraper().request
    try:
        resp = cget('get', info_link).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    if resp["success"]:
        return dl_link
    else:
        raise DirectDownloadLinkException(
            f"ERROR: {resp['message']}.")


def antfiles(url: str) -> str:
    """ Antfiles direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        link = Bypass().bypass_antfiles(url)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    if not link:
        raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")
    return link


def streamtape(url: str) -> str:
    """ Streamtape direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    splitted_url = url.split("/")
    _id = splitted_url[4] if len(splitted_url) >= 6 else splitted_url[-1]
    try:
        with requests.Session() as session:
            res = session.get(url)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    html = HTML(res.text)
    if not (script := html.xpath("//script[contains(text(),'ideoooolink')]/text()")):
        raise DirectDownloadLinkException("ERROR: Script tidak ditemukan!")
    if not (link := findall(r"(&expires\S+)'", script[0])):
        raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")
    return f"https://streamtape.com/get_video?id={_id}{link[-1]}"


def racaty(url):
    try:
        with create_scraper() as scraper:
            url = scraper.get(url).url
            json_data = {
                'op': 'download2',
                'id': url.split('/')[-1]
            }
            res = scraper.post(url, data=json_data)
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if (direct_link := HTML(res.text).xpath("//a[contains(@id,'uniqueExpirylink')]/@href")):
        return direct_link[0]
    else:
        raise DirectDownloadLinkException('ERROR: Link File tidak ditemukan!')


def fichier(link: str) -> str:
    """ 1Fichier direct link generator
    Based on https://github.com/Maujar
    """
    regex = r"^([http:\/\/|https:\/\/]+)?.*1fichier\.com\/\?.+"
    gan = match(regex, link)
    if not gan:
        raise DirectDownloadLinkException(
            "ERROR: Link 1Fichier tidak ditemukan!")
    if "::" in link:
        pswd = link.split("::")[-1]
        url = link.split("::")[-2]
    else:
        pswd = None
        url = link
    cget = create_scraper().request
    try:
        if pswd is None:
            req = cget('post', url)
        else:
            pw = {"pass": pswd}
            req = cget('post', url, data=pw)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    if req.status_code == 404:
        raise DirectDownloadLinkException(
            "ERROR: File tidak ditemukan!")
    soup = BeautifulSoup(req.content, 'lxml')
    if soup.find("a", {"class": "ok btn-general btn-orange"}):
        if dl_url := soup.find("a", {"class": "ok btn-general btn-orange"})["href"]:
            return dl_url
        raise DirectDownloadLinkException(
            "ERROR: Link File tidak ditemukan!")
    elif len(soup.find_all("div", {"class": "ct_warn"})) == 3:
        str_2 = soup.find_all("div", {"class": "ct_warn"})[-1]
        if "you must wait" in str(str_2).lower():
            if numbers := [int(word) for word in str(str_2).split() if word.isdigit()]:
                raise DirectDownloadLinkException(
                    f"ERROR: 1Fichier sedang limit! Silahkan tunggu {numbers[0]} menit lagi!")
            else:
                raise DirectDownloadLinkException(
                    "ERROR: 1Fichier sedang limit!")
        elif "protect access" in str(str_2).lower():
            raise DirectDownloadLinkException(
                f"ERROR:\n{PASSWORD_ERROR_MESSAGE.format(link)}")
        else:
            raise DirectDownloadLinkException(
                "ERROR: Link File tidak ditemukan!")
    elif len(soup.find_all("div", {"class": "ct_warn"})) == 4:
        str_1 = soup.find_all("div", {"class": "ct_warn"})[-2]
        str_3 = soup.find_all("div", {"class": "ct_warn"})[-1]
        if "you must wait" in str(str_1).lower():
            if numbers := [int(word) for word in str(str_1).split() if word.isdigit()]:
                raise DirectDownloadLinkException(
                    f"ERROR: 1Fichier sedang limit! Silahkan tunggu {numbers[0]} menit lagi!")
            else:
                raise DirectDownloadLinkException(
                    "ERROR: 1Fichier sedang limit!")
        elif "bad password" in str(str_3).lower():
            raise DirectDownloadLinkException(
                "ERROR: Password salah!")
        else:
            raise DirectDownloadLinkException(
                "ERROR: Link File tidak ditemukan!")
    else:
        raise DirectDownloadLinkException(
            "ERROR: Link File tidak ditemukan!")


def solidfiles(url: str) -> str:
    """ Solidfiles direct link generator
    Based on https://github.com/Xonshiz/SolidFiles-Downloader
    By https://github.com/Jusidama18 """
    cget = create_scraper().request
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
        }
        pageSource = cget('get', url, headers=headers).text
        mainOptions = str(
            search(r'viewerOptions\'\,\ (.*?)\)\;', pageSource).group(1))
        return loads(mainOptions)["downloadUrl"]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")


def krakenfiles(url):
    session = requests.Session()
    try:
        _res = session.get(url)
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    html = HTML(_res.text)
    if post_url:= html.xpath('//form[@id="dl-form"]/@action'):
        post_url = f'https:{post_url[0]}'
    else:
        session.close()
        raise DirectDownloadLinkException('ERROR: Link File tidak ditemukan!')
    if token:= html.xpath('//input[@id="dl-token"]/@value'):
        data = {'token': token[0]}
    else:
        session.close()
        raise DirectDownloadLinkException('ERROR: Link Token tidak ditemukan!')
    try:
        _json = session.post(post_url, data=data).json()
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if _json['status'] != 'ok':
        session.close()
        raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")
    session.close()
    return _json['url']


def uploadee(url: str) -> str:
    try:
        with requests.Session() as scraper:
            _res = scraper.get(url)
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if link := HTML(_res.text).xpath("//a[@id='d_l']/@href"):
        return link[0]
    else:
        raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")


def terabox(url) -> str:
    if not path.isfile('terabox.txt'):
        raise DirectDownloadLinkException("ERROR: Cookies (terabox.txt) tidak ditemukan!")
    try:
        jar = MozillaCookieJar('terabox.txt')
        jar.load()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    cookies = {}
    for cookie in jar:
        cookies[cookie.name] = cookie.value
    session = requests.Session()
    try:
        _res = session.get(url, cookies=cookies)
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')

    if jsToken := findall(r'window\.jsToken.*%22(.*)%22', _res.text):
        jsToken = jsToken[0]
    else:
        session.close()
        raise DirectDownloadLinkException('ERROR: jsToken tidak ditemukan!')
    shortUrl = parse_qs(urlparse(_res.url).query).get('surl')
    if not shortUrl:
        raise DirectDownloadLinkException("ERROR: Surl tidak ditemukan!")

    details = {'contents':[], 'title': '', 'total_size': 0}
    details["header"] = ' '.join(f'{key}: {value}' for key, value in cookies.items())

    def __fetch_links(dir_='', folderPath=''):
        params = {
            'app_id': '250528',
            'jsToken': jsToken,
            'shorturl': shortUrl
            }
        if dir_:
            params['dir'] = dir_
        else:
            params['root'] = '1'
        try:
            _json = session.get("https://www.1024tera.com/share/list", params=params, cookies=cookies).json()
        except Exception as e:
            raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
        if _json['errno'] not in [0, '0']:
            if 'errmsg' in _json:
                raise DirectDownloadLinkException(f"ERROR: {_json['errmsg']}")
            else:
                raise DirectDownloadLinkException('ERROR: Terjadi kesalahan!')

        if "list" not in _json:
            return
        contents = _json["list"]
        for content in contents:
            if content['isdir'] in ['1', 1]:
                if not folderPath:
                    if not details['title']:
                        details['title'] = content['server_filename']
                        newFolderPath = path.join(details['title'])
                    else:
                        newFolderPath = path.join(details['title'], content['server_filename'])
                else:
                    newFolderPath = path.join(folderPath, content['server_filename'])
                __fetch_links(content['path'], newFolderPath)
            else:
                if not folderPath:
                    if not details['title']:
                        details['title'] = content['server_filename']
                    folderPath = details['title']
                item = {
                    'url': content['dlink'],
                    'filename': content['server_filename'],
                    'path' : path.join(folderPath),
                }
                if 'size' in content:
                    size = content["size"]
                    if isinstance(size, str) and size.isdigit():
                        size = float(size)
                    details['total_size'] += size
                details['contents'].append(item)

    try:
        __fetch_links()
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(e)
    session.close()
    if len(details['contents']) == 1:
        return details['contents'][0]['url']
    return details


def filepress(url):
    cget = create_scraper().request
    try:
        url = cget('GET', url).url
        raw = urlparse(url)
        json_data = {
            'id': raw.path.split('/')[-1],
            'method': 'publicDownlaod',
        }
        api = f'{raw.scheme}://{raw.hostname}/api/file/downlaod/'
        res = cget('POST', api, headers={
                   'Referer': f'{raw.scheme}://{raw.hostname}'}, json=json_data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if 'data' not in res:
        raise DirectDownloadLinkException(f'ERROR: {res["statusText"]}')
    return f'https://drive.google.com/uc?id={res["data"]}&export=download'


def gdtot(url):
    cget = create_scraper().request
    try:
        res = cget('GET', f'https://gdbot.pro/file/{url.split("/")[-1]}')
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    token_url = HTML(res.text).xpath(
        "//a[contains(@class,'inline-flex items-center justify-center')]/@href")
    if not token_url:
        try:
            url = cget('GET', url).url
            p_url = urlparse(url)
            res = cget(
                "GET", f"{p_url.scheme}://{p_url.hostname}/ddl/{url.split('/')[-1]}")
        except Exception as e:
            raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
        if (drive_link := findall(r"myDl\('(.*?)'\)", res.text)) and "drive.google.com" in drive_link[0]:
            return drive_link[0]
        else:
            raise DirectDownloadLinkException(
                'ERROR: Link Drive tidak ditemukan!')
    token_url = token_url[0]
    try:
        token_page = cget('GET', token_url)
    except Exception as e:
        raise DirectDownloadLinkException(
            f'ERROR: {e.__class__.__name__} with {token_url}')
    path = findall('\("(.*?)"\)', token_page.text)
    if not path:
        raise DirectDownloadLinkException('ERROR: Tidak bisa membypass link!')
    path = path[0]
    raw = urlparse(token_url)
    final_url = f'{raw.scheme}://{raw.hostname}{path}'
    return sharer_scraper(final_url)


def sharer_scraper(url):
    cget = create_scraper().request
    try:
        url = cget('GET', url).url
        raw = urlparse(url)
        header = {
            "useragent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.548.0 Safari/534.10"}
        res = cget('GET', url, headers=header)
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    key = findall('"key",\s+"(.*?)"', res.text)
    if not key:
        raise DirectDownloadLinkException("ERROR: Kunci tidak ditemukan!")
    key = key[0]
    if not HTML(res.text).xpath("//button[@id='drc']"):
        raise DirectDownloadLinkException(
            "ERROR: Link File tidak ditemukan!")
    boundary = uuid4()
    headers = {
        'Content-Type': f'multipart/form-data; boundary=----WebKitFormBoundary{boundary}',
        'x-token': raw.hostname,
        'useragent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.548.0 Safari/534.10'
    }

    data = f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="action"\r\n\r\ndirect\r\n' \
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="key"\r\n\r\n{key}\r\n' \
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="action_token"\r\n\r\n\r\n' \
        f'------WebKitFormBoundary{boundary}--\r\n'
    try:
        res = cget("POST", url, cookies=res.cookies,
                   headers=headers, data=data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if "url" not in res:
        raise DirectDownloadLinkException(
            'ERROR: Link Drive tidak ditemukan!')
    if "drive.google.com" in res["url"]:
        return res["url"]
    try:
        res = cget('GET', res["url"])
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if (drive_link := HTML(res.text).xpath("//a[contains(@class,'btn')]/@href")) and "drive.google.com" in drive_link[0]:
        return drive_link[0]
    else:
        raise DirectDownloadLinkException(
            'ERROR: Link Drive tidak ditemukan!')


def wetransfer(url):
    cget = create_scraper().request
    try:
        url = cget('GET', url).url
        json_data = {
            'security_hash': url.split('/')[-1],
            'intent': 'entire_transfer'
        }
        res = cget(
            'POST', f'https://wetransfer.com/api/v4/transfers/{url.split("/")[-2]}/download', json=json_data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if "direct_link" in res:
        return res["direct_link"]
    elif "message" in res:
        raise DirectDownloadLinkException(f"ERROR: {res['message']}")
    elif "error" in res:
        raise DirectDownloadLinkException(f"ERROR: {res['error']}")
    else:
        raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")


def akmfiles(url):
    cget = create_scraper().request
    try:
        url = cget('GET', url).url
        json_data = {
            'op': 'download2',
            'id': url.split('/')[-1]
        }
        res = cget('POST', url, data=json_data)
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if (direct_link := HTML(res.text).xpath("//a[contains(@class,'btn btn-dow')]/@href")):
        return direct_link[0]
    else:
        raise DirectDownloadLinkException('ERROR: Link File tidak ditemukan!')


def shrdsk(url):
    cget = create_scraper().request
    try:
        url = cget('GET', url).url
        res = cget(
            'GET', f'https://us-central1-affiliate2apk.cloudfunctions.net/get_data?shortid={url.split("/")[-1]}')
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if res.status_code != 200:
        raise DirectDownloadLinkException(
            f'ERROR: Status Code {res.status_code}')
    res = res.json()
    if ("type" in res and res["type"].lower() == "upload" and "video_url" in res):
        return res["video_url"]
    raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")


def linkbox(url):
    cget = create_scraper().request
    try:
        url = cget('GET', url).url
        res = cget(
            'GET', f'https://www.linkbox.to/api/file/detail?itemId={url.split("/")[-1]}').json()
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if 'data' not in res:
        raise DirectDownloadLinkException('ERROR: Data tidak ditemukan!')
    data = res['data']
    if not data:
        raise DirectDownloadLinkException('ERROR: Data tidak ditemukan!')
    if 'itemInfo' not in data:
        raise DirectDownloadLinkException('ERROR: Item Info tidak ditemukan!')
    itemInfo = data['itemInfo']
    if 'url' not in itemInfo:
        raise DirectDownloadLinkException('ERROR: Link File tidak ditemukan!')
    if "name" not in itemInfo:
        raise DirectDownloadLinkException(
            'ERROR: Nama File tidak ditemukan!')
    name = quote(itemInfo["name"])
    raw = itemInfo['url'].split("/", 3)[-1]
    return f'https://wdl.nuplink.net/{raw}&filename={name}'


def gofile(url):
    try:
        if "::" in url:
            _password = url.split("::")[-1]
            _password = sha256(_password.encode("utf-8")).hexdigest()
            url = url.split("::")[-2]
        else:
            _password = ''
        _id = url.split("/")[-1]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")

    session = requests.Session()

    def __get_token():
        if 'gofile_token' in _caches:
            __url = f"https://api.gofile.io/getAccountDetails?token={_caches['gofile_token']}"
        else:
            __url = 'https://api.gofile.io/createAccount'
        try:
            __res = session.get(__url, verify=False).json()
            if __res["status"] != 'ok':
                if 'gofile_token' in _caches:
                    del _caches['gofile_token']
                return __get_token()
            _caches['gofile_token'] = __res["data"]["token"]
            return _caches['gofile_token']
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")

    try:
        token = __get_token()
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(e)
    
    details = {'contents':[], 'title': '', 'total_size': 0}
    headers = {"Cookie": f"accountToken={token}"}
    details["header"] = ' '.join(f'{key}: {value}' for key, value in headers.items())

    def __fetch_links(_id, folderPath=''):
        _url = f"https://api.gofile.io/getContent?contentId={_id}&token={token}&websiteToken=7fd94ds12fds4&cache=true"
        if _password:
            _url += f"&password={_password}"
        try:
            _json = session.get(_url, verify=False).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
        if _json['status'] in 'error-passwordRequired':
            raise DirectDownloadLinkException(f'ERROR: Link File ini memerlukan password!\nTambahkan password dengan menambahkan tanda :: setelah link dan masukan password setelah tanda :: tanpa menggunakan spasi (Password bisa menggunakan spasi)!\n\nContoh :\n{url}::ini password')
        if _json['status'] in 'error-passwordWrong':
            raise DirectDownloadLinkException('ERROR: Password salah!')
        if _json['status'] in 'error-notFound':
            raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")
        if _json['status'] in 'error-notPublic':
            raise DirectDownloadLinkException("ERROR: Folder tidak dapat diunduh!")

        data = _json["data"]

        if not details['title']:
            details['title'] = data['name'] if data['type'] == "folder" else _id

        contents = data["contents"]
        for content in contents.values():
            if content["type"] == "folder":
                if not content['public']:
                    continue
                if not folderPath:
                    newFolderPath = path.join(details['title'], content["name"])
                else:
                    newFolderPath = path.join(folderPath, content["name"])
                __fetch_links(content["id"], newFolderPath)
            else:
                if not folderPath:
                    folderPath = details['title']
                item = {
                    "path": path.join(folderPath),
                    "filename": content["name"],
                    "url": content["link"],
                }
                if 'size' in content:
                    size = content["size"]
                    if isinstance(size, str) and size.isdigit():
                        size = float(size)
                    details['total_size'] += size
                details['contents'].append(item)

    try:
        __fetch_links(_id)
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(e)
    session.close()
    if len(details['contents']) == 1:
        return (details['contents'][0]['url'], details['header'])
    return details


def cf_bypass(url):
    "DO NOT ABUSE THIS"
    try:
        data = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": 60000
        }
        _json = requests.post("https://cf.jmdkh.eu.org/v1", headers={"Content-Type": "application/json"}, json=data).json()
        if _json['status'] == 'ok':
            return _json['solution']["response"]
    except Exception as e:
        e
    raise DirectDownloadLinkException("ERROR: Tidak bisa bypass CloudFlare!")


def send_cm_file(url, file_id=None):
    if "::" in url:
        _password = url.split("::")[-1]
        url = url.split("::")[-2]
    else:
        _password = ''
    _passwordNeed = False
    with create_scraper() as session:
        if file_id is None:
            try:
                html = HTML(session.get(url).text)
            except Exception as e:
                raise DirectDownloadLinkException(
                    f'ERROR: {e.__class__.__name__}')
            if html.xpath("//input[@name='password']"):
                _passwordNeed = True
            if not (file_id := html.xpath("//input[@name='id']/@value")):
                raise DirectDownloadLinkException('ERROR: Link File tidak ditemukan!')
        try:
            data = {'op': 'download2', 'id': file_id}
            if _password and _passwordNeed:
                data["password"] = _password
            _res = session.post('https://send.cm/', data=data, allow_redirects=False)
            if 'Location' in _res.headers:
                return (_res.headers['Location'], 'Referer: https://send.cm/')
        except Exception as e:
            raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if _passwordNeed:
        raise DirectDownloadLinkException(f"ERROR:\n{PASSWORD_ERROR_MESSAGE.format(url)}")
    raise DirectDownloadLinkException("ERROR: Direct Link tidak ditemukan!")


def send_cm(url: str):
    if '/d/' in url:
        return send_cm_file(url)
    elif '/s/' not in url:
        file_id = url.split("/")[-1]
        return send_cm_file(url, file_id)
    splitted_url = url.split("/")
    details = {'contents': [], 'title': '', 'total_size': 0,
               'header': 'Referer: https://send.cm/'}
    if len(splitted_url) == 5:
        url += '/'
        splitted_url = url.split("/")
    if len(splitted_url) >= 7:
        details['title'] = splitted_url[5]
    else:
        details['title'] = splitted_url[-1]
    session = requests.Session()

    def __collectFolders(html):
        folders = []
        folders_urls = html.xpath('//h6/a/@href')
        folders_names = html.xpath('//h6/a/text()')
        for folders_url, folders_name in zip(folders_urls, folders_names):
            item = {}
            item['folder_link'] = folders_url.strip()
            item['folder_name'] = folders_name.strip()
            folders.append(item)
        return folders

    def __getFile_link(file_id):
        try:
            _res = session.post(
                'https://send.cm/', data={'op': 'download2', 'id': file_id}, allow_redirects=False)
            if 'Location' in _res.headers:
                return _res.headers['Location']
        except:
            pass

    def __getFiles(html):
        files = []
        hrefs = html.xpath('//tr[@class="selectable"]//a/@href')
        file_names = html.xpath('//tr[@class="selectable"]//a/text()')
        sizes = html.xpath('//tr[@class="selectable"]//span/text()')
        for href, file_name, size_text in zip(hrefs, file_names, sizes):
            item = {}
            item['file_id'] = href.split('/')[-1]
            item['filename'] = file_name.strip()
            item['size'] = text_size_to_bytes(size_text.strip())
            files.append(item)
        return files

    def __writeContents(html_text, folderPath=''):
        folders = __collectFolders(html_text)
        for folder in folders:
            _html = HTML(cf_bypass(folder['folder_link']))
            __writeContents(_html, path.join(folderPath, folder['folder_name']))
        files = __getFiles(html_text)
        for file in files:
            if not (link := __getFile_link(file['file_id'])):
                continue
            item = {'url': link,
                    'filename': file['filename'], 'path': folderPath}
            details['total_size'] += file['size']
            details['contents'].append(item)
    try:
        mainHtml = HTML(cf_bypass(url))
    except DirectDownloadLinkException as e:
        session.close()
        raise e
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__} ketika mencoba mendapatkan Link!")
    try:
        __writeContents(mainHtml, details['title'])
    except DirectDownloadLinkException as e:
        session.close()
        raise e
    except Exception as e:
        session.close()
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__} ketika mencoba mendapatkan Konten!")
    session.close()
    if len(details['contents']) == 1:
        return (details['contents'][0]['url'], details['header'])
    return details


def doods(url: str):
    if "/e/" in url:
        url = url.replace("/e/", "/d/")
    parsed_url = urlparse(url)
    session = create_scraper()
    try:
        _res = session.get(url)
        html = HTML(_res.text)
    except Exception as e:
        raise DirectDownloadLinkException(
            f'ERROR: {e.__class__.__name__} ketika mencoba mendapatkan Token!')
    if not (link := html.xpath("//div[@class='download-content']//a/@href")):
        raise DirectDownloadLinkException('ERROR: Token Link tidak ditemukan!')
    link = f'{parsed_url.scheme}://{parsed_url.hostname}/{link[0]}'
    try:
        _res = session.get(link)
    except Exception as e:
        raise DirectDownloadLinkException(
            f'ERROR: {e.__class__.__name__} ketika mencoba mendapatkan Direct Link!')
    if not (link := search(r"window\.open\('(\S+)'", _res.text)):
        raise DirectDownloadLinkException("ERROR: Direct Link tidak ditemukan!")
    return (link.group(1), f'Referer: {parsed_url.scheme}://{parsed_url.hostname}/')


def easyupload(url):
    if "::" in url:
        _password = url.split("::")[-1]
        url = url.split("::")[-2]
    else:
        _password = ''
    file_id = url.split("/")[-1]
    with create_scraper() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
        first_page_html = HTML(_res.text)
        if first_page_html.xpath("//h6[contains(text(),'Password Protected')]") and not _password:
            raise DirectDownloadLinkException(f"ERROR:\n{PASSWORD_ERROR_MESSAGE.format(url)}")
        if not (match := search(r'https://eu(?:[1-9][0-9]?|100)\.easyupload\.io/action\.php', _res.text)):
            raise DirectDownloadLinkException("ERROR: Link EasyUpload tidak ditemukan!")
        action_url = match.group()
        session.headers.update({'referer': 'https://easyupload.io/'})
        recaptcha_params = {
            'k': '6LfWajMdAAAAAGLXz_nxz2tHnuqa-abQqC97DIZ3',
            'ar': '1',
            'co': 'aHR0cHM6Ly9lYXN5dXBsb2FkLmlvOjQ0Mw..',
            'hl': 'en',
            'v': '0hCdE87LyjzAkFO5Ff-v7Hj1',
            'size': 'invisible',
            'cb': 'c3o1vbaxbmwe'
        }
        if not (captcha_token :=get_captcha_token(session, recaptcha_params)):
            raise DirectDownloadLinkException('ERROR: Token Captcha tidak ditemukan!')
        try:
            data = {'type': 'download-token',
                    'url': file_id,
                    'value': _password,
                    'captchatoken': captcha_token,
                    'method': 'regular'}
            json_resp = session.post(url=action_url, data=data).json()
        except Exception as e:
            raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if 'download_link' in json_resp:
        return json_resp['download_link']
    elif 'data' in json_resp:
        raise DirectDownloadLinkException(
            f"ERROR: {json_resp['data']}")
    raise DirectDownloadLinkException(
        "ERROR: Direct Link tidak ditemukan!")


# NOTE: Added from other repositories

def mp4upload(url: str) -> str:
    import urllib3
    url = url.replace("embed-", "")
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0", "Referer": "https://www.mp4upload.com/"}
    req = session.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    inputs = soup.find_all("input")
    data = {input.get("name"): input.get("value") for input in inputs}
    if not data:
        raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")
    post = session.post(url, data=data, headers=headers)
    soup = BeautifulSoup(post.text, "lxml")
    inputs = soup.find_all("form", {"name": "F1"})[0].find_all("input")
    data = {input.get("name"): input.get("value").replace(" ", "") for input in inputs}
    if not data:
        raise DirectDownloadLinkException("ERROR: Link File tidak ditemukan!")
    data["referer"] = url
    urllib3.disable_warnings()
    link = session.post(url, data=data, verify=False).url
    return link
    

def androiddatahost(url: str) -> str:
    try:
        ases = create_scraper()
        link = findall(r"\bhttps?://androiddatahost\.com\S+", url)[0]
        url3 = BeautifulSoup(ases.get(link).content, "html.parser")
        fin = url3.find("div", {"download2"})
        return fin.find("a")["href"]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    

def apkadmin(url: str) -> str:
    try:
        scraper = create_scraper()
        r = scraper.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        op = soup.find("input", {"name": "op"})["value"]
        ids = soup.find("input", {"name": "id"})["value"]

        data = {
            "op": op,
            "id": ids,
            "rand": " ",
            "referer": " ",
            "method_free": " ",
            "method_premium": " ",
        }
        dlnk = scraper.post(url, data=data)
        dbsop = BeautifulSoup(dlnk.text, "lxml")
        dl = dbsop.find("div", {"class": "text text-center"})
        return dl.find("a")["href"]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    

def sourceforge(url: str) -> str:
    if "master.dl.sourceforge.net" in url:
        return f"{url}?viasf=1"
    if url.endswith("/download"):
        url = url.split("/download")[0]
    try:
        link = findall(r"\bhttps?://sourceforge\.net\S+", url)[0]
    except IndexError:
        raise DirectDownloadLinkException("ERROR: Link SourceForge tidak ditemukan!")
    file_path = findall(r"files(.*)", link)[0]
    project = findall(r"projects?/(.*?)/files", link)[0]
    mirrors = f"https://sourceforge.net/settings/mirror_choices?projectname={project}&filename={file_path}"
    page = BeautifulSoup(requests.get(mirrors).content, "html.parser")
    info = page.find("ul", {"id": "mirrorList"}).findAll("li")
    try:
        for mirror in info[1:]:
            dl_url = f'https://{mirror["id"]}.dl.sourceforge.net/project/{project}/{file_path}?viasf=1'
        return dl_url
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")


def androidfilehost(url: str) -> str:
    try:
        link = findall(r"\bhttps?://.*androidfilehost.*fid.*\S+", url)[0]
    except IndexError:
        raise DirectDownloadLinkException("ERROR: Link AndroidFileHost tidak ditemukan!")
    fid = findall(r"\?fid=(.*)", link)[0]
    res = requests.get(link)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": f"https://androidfilehost.com/?fid={fid}",
        "X-MOD-SBB-CTYPE": "xhr",
        "X-Requested-With": "XMLHttpRequest",
    }
    data = {"submit": "submit", "action": "getdownloadmirrors", "fid": fid}
    mirrors = None
    try:
        req = requests.post("https://androidfilehost.com/libs/otf/mirrors.otf.php", headers=headers, data=data, cookies=res.cookies)
        mirrors = req.json()["MIRRORS"]
    except (json.decoder.JSONDecodeError, TypeError):
        raise DirectDownloadLinkException("ERROR: Link AndroidFileHost tidak ditemukan!")
    if mirrors is None:
        raise DirectDownloadLinkException("ERROR: Link AndroidFileHost tidak ditemukan!")
    for i in mirrors:
        link = i["url"]
        if link:
            break
    return link


def tusfiles(url: str) -> str:
    try:
        ses = create_scraper()
        res = ses.get(url)
        burl = "https://tusfiles.com/"
        headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }
        client = BeautifulSoup(res.text, "lxml")
        inputs = client.find_all("input")
        file_id = inputs[1]["value"]
        # file_name = findall("URL=(.*?) - ", res.text)[0].split("]")[1]
        parse = {"op": "download2", "id": file_id, "referer": url}
        resp2 = ses.post(burl, data=parse, headers=headers, allow_redirects=False)
        if jcok:= resp2.headers["location"]:
            return jcok
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    

def pandafiles(url: str) -> str:
    try:
        scraper = create_scraper()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0", "Referer": url, "X-Requested-With": "XMLHttpRequest"}
        media_id = search(r"(?://|\.)(pandafiles\.com)/([0-9a-zA-Z]+)", url)[2]
        data = {"op": "download2", "usr_login": "", "id": media_id, "referer": url, "method_free": "Free Download"}
        req = scraper.post(url, headers=headers, data=data)
        return BeautifulSoup(req.content, "lxml").find("div", {"id": "direct_link"}).find("a")["href"]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    

def uploadhaven(link: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"}
    test = BeautifulSoup(requests.get(link, headers=headers).text, "lxml")
    d = test.find("div", {"class": "alert alert-danger col-md-12"})
    if d is not None:
        hot1 = test.find("div", {"class": "alert alert-danger col-md-12"})
        hot_text = hot1.text.strip()
        raise DirectDownloadLinkException(f"ERROR: {str(hot_text)}")
    else:
        try:
            data = {
                "_token": test.find("input", {"name": "_token"})["value"],
                "key": test.find("input", {"name": "key"})["value"],
                "time": test.find("input", {"name": "time"})["value"],
                "hash": test.find("input", {"name": "hash"})["value"],
                "type": "free",
            }
            for _ in range(6, 0, -1):
                sleep(1)
            reurl = BeautifulSoup(requests.post(link, headers=headers, data=data).text, "lxml")
            return reurl.find("div", class_="alert alert-success mb-0").find("a")["href"]
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")


def uploadrar(url: str) -> str:
    try:
        url1 = url.strip("/ ")
        file_id = url1.split("/")[-1]
        headers = {"Referer": url}
        data = {
            "op": "download2",
            "id": file_id,
            "rand": "",
            "method_free": "Free Download",
            "method_premium": "",
        }
        req = requests.post(url, data=data, headers=headers)
        bs = BeautifulSoup(req.text, "lxml")
        return bs.find("span", {"id": "direct_link"}).find("a").get("href")
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
    

def romsget(url: str) -> str:
    try:
        req = requests.get(url)
        bs1 = BeautifulSoup(req.text, "html.parser")

        upos = bs1.find("form", {"id": "download-form"}).get("action")
        meid = bs1.find("input", {"id": "mediaId"}).get("name")
        try:
            dlid = bs1.find("button", {"data-callback": "onDLSubmit"}).get("dlid")
        except:
            dlid = bs1.find("div", {"data-callback": "onDLSubmit"}).get("dlid")

        pos = requests.post("https://www.romsget.io" + upos, data={meid: dlid})
        bs2 = BeautifulSoup(pos.text, "html.parser")
        udl = bs2.find("form", {"name": "redirected"}).get("action")
        prm = bs2.find("input", {"name": "attach"}).get("value")
        return f"{udl}?attach={prm}"
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")


def hexupload(url) -> str:
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us,en;q=0.6",
        "Sec-Fetch-Mode": "navigate",
    }
    payload = {
        "op": "download2",
        "id": url.split("/")[-1],
        "rand": "",
        "referer": url,
        "method_free": "Free Download",
    }
    try:
        html = requests.post(url, data=payload, headers=head)
        url = search(r"ldl.ld\('([^']+)", html.text)
        if url:
            url = b64decode(url.group(1)).decode("utf-8").replace(" ", "%20")
            return url
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")

""" 
def doodstream(url: str) -> str:
    DoodStream direct link generator
    Scrapped by https://github.com/arakurumi
    NOTE: Working on my machine, not work in vps (digitalocean) and heroku
    TODO: Rescrape with better method (This method sometimes got Cloudflare version 2 Captcha challenge)

    base_url = "https://dood.yt"
    headers = "Referer: https://dood.yt/"
    cget = create_scraper(
        browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }).request
    for domain in dood_sites:
        url = url.replace(domain, "dood.yt")
    if "/e/" in url:
        url = url.replace("/e/", "/d/")
    if "/f/" in url:
        url = url.replace("/f/", "/d/")
    page_resp = cget('GET', url)
    # Force get url when not 200 response
    while "200" not in str(page_resp):
        try:
            page_resp = cget('GET', url)
        except:
            pass
    soup = BeautifulSoup(page_resp.text, "lxml")
    try:
        dl_link = soup.find_all("a", {"class": "btn btn-primary d-flex align-items-center justify-content-between"})
        for link in dl_link:
            dl_link = link['href']
        if len(dl_link) == 0:
            raise DirectDownloadLinkException(f"ERROR: Link ini tidak memliki tombol unduh!")
    except:
        raise DirectDownloadLinkException(f"ERROR: Link ini tidak memliki tombol unduh!")
    dl_page_resp = cget('GET', base_url + dl_link)
    soup = BeautifulSoup(dl_page_resp.text, "lxml")
    # Force get url when security error
    while "Security error" in str(soup):
        try:
            dl_page_resp = cget('GET', base_url + dl_link)
            soup = BeautifulSoup(dl_page_resp.text, "lxml")
        except:
            pass
    try:
        ddl_link = soup.find_all("a", {"class": "btn btn-primary d-flex align-items-center justify-content-between"})
        for link in ddl_link:
            ddl_link = link["onclick"]
        ddl_link = ddl_link.split("'")[1].split("'")[-1]
        if "http" not in ddl_link:
            return base_url + ddl_link, headers
        else:
            return ddl_link, headers
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
"""

def pake(url: str) -> str:
    """
    URL : https://api.pake.tk
    Supported Sites :
    - Dood (Slow)
    - Vidstream (Untested)
    """

    base = "https://dd-cdn.pakai.eu.org/download?url="  # For bypass different IP
    req = requests.get(f"https://api.pake.tk/dood?url={url}")
    if req.status_code != 200:
        raise DirectDownloadLinkException(f'ERROR: Gagal mendapatkan direct link!')
    else:
        try:
            req = req.json()

            details = {'contents':[], 'title': '', 'total_size': 0}

            details['title'] = f"{req['data']['title']}.mp4"

            item = {
                "path": path.join(details['title']),
                "filename": details['title'],
                "url": f"{base}{req['data']['direct_link']}&title={details['title']}.mp4",
            }
       
            details["contents"].append(item)
        except ValueError:
            raise DirectDownloadLinkException(f'ERROR: Gagal mendapatkan direct link!')
    return details

"""
def nurlresolver(url: str) -> str:
    NOTE:
    There're many sites supported by this api
    You can check supported sites here :
    https://github.com/mnsrulz/nurlresolver/tree/master/src/libs

    req = requests.get(f"https://nurlresolver.netlify.app/.netlify/functions/server/resolve?q={url}&m=&r=false")
    if req.status_code != 200:
        raise DirectDownloadLinkException(f'ERROR: Gagal mendapatkan direct link!')
    try:
        req = req.json()
        if len(req) == 0:
            raise DirectDownloadLinkException(f'ERROR: Gagal mendapatkan direct link!')
        
        details = {'contents':[], 'title': '', 'total_size': 0}
        
        for file in req:
            headers = file["headers"]
            details["header"] = ' '.join(f'{key}: {value}' for key, value in headers.items())
            
            details['title'] = file["title"]
            
            item = {
                "path": path.join(details['title']),
                "filename": details['title'],
                "url": file["link"],
            }
            
            size = file["size"]
            if isinstance(size, str) and size.isdigit():
                size = float(size)
            details["total_size"] += size

            details["content"].append(item)
    except ValueError:
        raise DirectDownloadLinkException(f'ERROR: Gagal mendapatkan direct link!')
    return details
"""
