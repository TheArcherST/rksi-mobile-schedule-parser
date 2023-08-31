import asyncio

from .base_parser import BaseScheduleParser


class ScheduleParsingController:
    def __init__(self,
                 parser: BaseScheduleParser):

        self.parser = parser

    async def run(self):
        await asyncio.sleep(1)
