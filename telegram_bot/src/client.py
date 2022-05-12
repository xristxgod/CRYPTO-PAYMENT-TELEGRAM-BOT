import io
import time
import typing

import aiohttp

class ConfigAPI:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ConfigAPI, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        time.sleep(15)
        jar = aiohttp.CookieJar(unsafe=True, quote_cookie=False)
        self.session = aiohttp.ClientSession(cookie_jar=jar)

    def __del__(self):
        self.session.close()

api = ConfigAPI()

async def raw_get(url: str, **kwargs):
    params = "&".join([f"{k}={v}" for k, v in kwargs.items()])
    return await api.session.get(f"{url}?{params}")

async def raw_post(url: str, data):
    return await api.session.post(url, json=data)

async def get_file_content(url: str) -> typing.Optional[io.BytesIO]:
    resp = await api.session.get(url)
    if not resp.ok:
        return None
    return io.BytesIO(await resp.read())