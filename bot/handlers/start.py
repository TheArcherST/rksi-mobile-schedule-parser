from aiogram.types import Message
from aiogram.dispatcher.filters.state import StatesGroup, State

from bot.config import dp

from utils import FsmNamespace


class StartNamespace(FsmNamespace):
    group: str


class StartForm(StatesGroup):
    enter_group = State()


@dp.message_handler(commands=['start'])
async def start_handler(message: Message):
    await message.answer('Привет! Введи свою группу (например <code>ИБА-11</code>)')
    await StartForm.enter_group.set()


@dp.message_handler(state=StartForm.enter_group.state)
async def group_handler(message: Message):
    async with StartNamespace() as proxy:
        proxy.group = message.text

    await message.answer('Группа')
