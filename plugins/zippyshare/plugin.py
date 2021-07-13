__all__ = ['ZippySharePlugin']

from os.path import basename
from re import findall
from typing import Optional

from pyquery import PyQuery

from app import Plugin


class ZippySharePlugin(Plugin):
    URL_REGEX = f'^https?://(.*?)\.zippyshare\.com/v/(.*?)/file.html$'
    # noinspection SpellCheckingInspection
    SCRIPT_REGEX = r'document\.getElementById\([\'"]dlbutton[\'"]\)\.href\s*=\s*[\'"]/d/(.*?)/[\'"]\s*\+\s*\(([0-9 %+\-*/]*?)\)\s*\+\s*[\'"]/(.*?)[\'"];'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = None

    def attack(self) -> None:
        server_id, file_id = self.id
        # noinspection SpellCheckingInspection
        res = self.client.get(f'https://{server_id}.zippyshare.com/v/{file_id}/file.html')
        pq = PyQuery(res.content)
        for script in pq('script'):
            if script.text:
                try:
                    _file_id, challenge, path = findall(self.SCRIPT_REGEX, script.text).pop()
                    assert file_id == _file_id
                    challenge = eval(challenge)
                    # noinspection SpellCheckingInspection
                    self.url = f'https://{server_id}.zippyshare.com/d/{file_id}/{challenge}/{path}'
                    self.name = basename(self.url)
                    break
                except IndexError:
                    pass

    def parse_url(self, url: str) -> Optional[str]:
        try:
            return findall(self.URL_REGEX, url).pop()
        except IndexError:
            pass

    def download(self, path) -> None:
        return self._download(self.url, path)
