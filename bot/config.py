from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.files import JSONStorage

from config import config


bot = Bot(config.bot_token, parse_mode=ParseMode.HTML)
storage = JSONStorage(config.userflow_path)
dp = Dispatcher(bot=bot, storage=storage)
