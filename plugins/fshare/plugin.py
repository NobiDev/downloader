__all__ = ['FSharePlugin']

from datetime import datetime
from re import findall
from time import sleep
from typing import Optional, Tuple

from pyquery import PyQuery

from app import Plugin


class FSharePlugin(Plugin):
    BASE_URL = 'https://www.fshare.vn'
    URL_REGEX = f'^{BASE_URL}/file/(.*?)(?:\?.*)?$'
    GET_URL = f'{BASE_URL}/download/get'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csrf_param, self.csrf_token = self.get_csrf()
        self.url = None
        self.wait_time = 0
        self.extra = None

    def attack(self) -> None:
        # noinspection SpellCheckingInspection
        res = self.client.post(self.GET_URL, data={
            self.csrf_param: self.csrf_token,
            'linkcode': self.id,
            'withFcode5': 0,
            # 'fcode': '',
        })
        data = res.json()
        self.name = data.get('name')
        self.url = data.get('url')
        self.wait_time = datetime.now().timestamp() + data.get('wait_time')
        self.extra = data.get('extra')

    def parse_url(self, url: str) -> Optional[str]:
        try:
            return findall(self.URL_REGEX, url).pop()
        except IndexError:
            pass

    def get_csrf(self) -> Tuple[str, str]:
        res = self.client.get(self.BASE_URL)
        pq = PyQuery(res.content)
        param = pq('meta[name=csrf-param]').attr('content')
        token = pq('meta[name=csrf-token]').attr('content')
        return param, token

    def download(self, path) -> None:
        while self.wait_time > datetime.now().timestamp():
            wait_time = int(self.wait_time - datetime.now().timestamp())
            print(f'[-] Wait {wait_time}s')
            sleep(1)
        return self._download(self.url, path)
