from typing import TypeVar, Generic

from aiogram import Dispatcher


_T = TypeVar('_T')


class FsmNamespace:
    """FsmNamespace

    Designed to encapsulate results of some dialog part within object.

    """

    def __init__(self, data=None):
        self._data = data
        self._root = self.__class__.__name__

    def __getattr__(self, item):
        if item.startswith('_'):
            return super().__getattribute__(item)
        else:
            return self._data.get(self._root, {}).get(item)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            return super().__setattr__(key, value)
        else:
            return self._data[self._root].update({key: value})

    async def _load(self, data=None):
        if data is not None:
            self._data = data

        dp = Dispatcher.get_current()
        fsm_context = dp.current_state()
        data = await fsm_context.get_data()
        self._data = data

        if self._root not in self._data:
            self._data[self._root] = {}

        return self

    async def _save(self):
        await self._meta.fsm_context.set_data(self._data)

    async def __aenter__(self):
        await self._load(self._meta)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._save()
