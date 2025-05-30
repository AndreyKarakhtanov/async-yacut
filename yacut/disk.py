
import asyncio
import urllib

import aiohttp

from . import app

AUTH_HEADERS = {
    'Authorization': f'OAuth {app.config["DISK_TOKEN"]}'
}
API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


async def upload_files_and_get_url(files):
    if files is not None:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for file in files:
                tasks.append(
                    asyncio.ensure_future(
                        upload_file_to_disk_and_get_url(session, file)
                    )
                )
            paths = await (asyncio.gather(*tasks))
        return paths


async def upload_file_to_disk_and_get_url(session, file):
    payload = {
        'path': f'app:/{file.filename}',
        'overwrite': 'True'
    }
    async with session.get(
        headers=AUTH_HEADERS,
        params=payload,
        url=REQUEST_UPLOAD_URL
    ) as response:
        upload_url = (await response.json())['href']
        data = file.read()
    async with session.put(
        data=data,
        url=upload_url,
    ) as response:
        location = response.headers['Location']
        location = urllib.parse.unquote(location)
        location = location.replace('/disk', '')
    return location


async def get_download_file_url(path):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            headers=AUTH_HEADERS,
            url=DOWNLOAD_LINK_URL,
            params={'path': f'{path}'}
        ) as response:
            link = (await response.json())['href']
            return link