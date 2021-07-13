__all__ = ['Application']

from importlib import import_module
from os.path import exists
from re import match
from urllib.parse import urlparse

from .plugin import Plugin, plugins


class Application:
    def __init__(self):
        self.load_modules()

    @classmethod
    def load_modules(cls):
        import_module('plugins')

    @staticmethod
    def get_plugin(url) -> Plugin:
        for plugin_cls in plugins:
            try:
                plugin = plugin_cls(url)
                return plugin
            except AssertionError:
                pass

    def run(self, *args: str) -> None:
        for arg in args:
            self._run(arg)

    def _run(self, item: str) -> None:
        if match(r'^https?://', item):
            return self._run_url(item)
        if exists(item):
            return self._run_file(item)
        print(f'[Warning] Cannot parse parameter type of {item}')

    def _run_file(self, path: str) -> None:
        print(f'[-] Processing File: {path}')
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    self._run(line)

    def _run_url(self, url: str) -> None:
        print(f'[-] Processing URL: {url}')
        plg = self.get_plugin(url)
        if not plg:
            print(f'[Error] No plugin found for {urlparse(url).hostname}')
            return
        plg.attack()
        if not plg.name:
            print(f'[Error] Unable to download {plg.id}')
        print(f'[-] Name: {plg.name}')
        if plg.name and exists(plg.name):
            print(f'[-] File already exists, skip the download')
            return
        plg.download(plg.name)
