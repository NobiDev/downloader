__all__ = ['plugins', 'Plugin']

from abc import ABC, abstractmethod
from typing import List, Optional

from requests import Session
from requests.models import CONTENT_CHUNK_SIZE

plugins: List[type] = []


class Plugin(ABC):
    @classmethod
    def __init_subclass__(cls, **kwargs) -> None:
        plugins.append(cls)

    def __init__(self, url: str) -> None:
        self.id = self.parse_url(url)
        assert self.id
        self.name = None
        self.client = Session()

    @abstractmethod
    def parse_url(self, url: str) -> Optional[str]:
        pass

    @abstractmethod
    def attack(self) -> None:
        pass

    @abstractmethod
    def download(self, path: str) -> None:
        pass

    def _download(self, url: str, path: str) -> None:
        print(f'[-] Download from {url}')
        with self.client.get(url, stream=True, allow_redirects=False) as res:
            res.raise_for_status()
            if res.is_redirect:
                print(f'[-] Redirecting to {res.next.url}')
                return self._download(res.next.url, path)
            if 'text/html' in res.headers.get('Content-Type'):
                print('[-] Download failed !')
                return
            size = int(res.headers.get('Content-Length') or 0)
            if size:
                print(f'[-] Size: {size // 1024 * 100 // 1024 / 100} MB')
            print(f'[-] Save to: {path}')
            print('[-] Downloading ...')
            downloaded_size = 0
            with open(path, 'wb') as f:
                for chunk in res.iter_content(chunk_size=CONTENT_CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                    print(f'[-] Downloading ... {downloaded_size * 100 // size} %')
