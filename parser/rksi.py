import copy
import urllib.parse
from typing import Iterable, Any
from dataclasses import dataclass

from datetime import datetime, date

from rutimeparser import parse as ru2date

from aiohttp import ClientSession
from aiohttp.client_exceptions import ServerTimeoutError

from bs4 import BeautifulSoup
from bs4.element import Tag, PageElement

from .base_parser import BaseScheduleParser, BadResponse
from .models import RawSubjectEntry


class TokenType:
    THEME = 'THEME'
    DATE = 'DATE'
    START_TIME = 'START_TIME'
    END_TIME = 'END_TIME'
    TEACHER = 'TEACHER'
    AUDIENCE_NUMBER = 'AUDIENCE_NUMBER'
    END_OF_THEME = 'END_OF_THEME'


@dataclass
class Token:
    type: str
    value: Any


class ThemesFromPageElements:
    def __init__(self, page_elements: Iterable[PageElement]):
        self._elements = iter(page_elements)
        self._generator = self.tokens_generator()

    def themes_generator(self):
        current = RawSubjectEntry()

        while True:
            try:
                token = self._generator.__next__()
            except StopIteration:
                break

            if token.type == TokenType.START_TIME:
                current.starts_at = token.value
            elif token.type == TokenType.END_TIME:
                current.ends_at = token.value
            elif token.type == TokenType.THEME:
                current.name = token.value
            elif token.type == TokenType.TEACHER:
                current.teacher = token.value
            elif token.type == TokenType.DATE:
                current.date = token.value
            elif token.type == TokenType.AUDIENCE_NUMBER:
                current.audience = token.value
            elif token.type == TokenType.END_OF_THEME:
                yield current
            else:
                raise KeyError(f"Can't handle token {token!r}")

    # TODO: represent following tokenizing logic as data, because this algorithm can change many times

    def tokens_generator(self):
        for i in self._elements:
            if isinstance(i, Tag):
                if i.name == 'p':
                    try:
                        yield from self._parse_p(i)
                    except (KeyError, TypeError):
                        pass
                    else:
                        yield Token(TokenType.END_OF_THEME, '')
                elif i.name == 'b':
                    yield Token(TokenType.DATE, ru2date(i.text.split(',')[0]))
        else:
            return

    def _parse_p(self, p: Tag):
        if p.name != 'p':
            raise RuntimeError()

        children = list(p.children)

        time_range_s = children[0]

        start_time_s, end_time_s = time_range_s.split('—')

        yield Token(TokenType.START_TIME, datetime.strptime(start_time_s.strip(), '%H:%M').time())
        yield Token(TokenType.END_TIME, datetime.strptime(end_time_s.strip(), '%H:%M').time())

        yield Token(TokenType.THEME, children[2].text)

        try:
            teacher, audience = children[4].text.split(', ауд. ')
        except IndexError:
            pass
        else:
            yield Token(TokenType.TEACHER, teacher)
            yield Token(TokenType.AUDIENCE_NUMBER, audience)


class RKSIScheduleParser(BaseScheduleParser):
    async def is_alive(self, timeout: float = 10) -> bool:
        async with ClientSession(conn_timeout=timeout) as session:

            try:
                r = await session.get('https://rksi.ru/mobile_schedule')
            except ServerTimeoutError:
                return False
            else:
                return r.status // 100 == 2

    async def parse_group_themes(self, group_name: str) -> list[RawSubjectEntry]:
        async with ClientSession() as session:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://rksi.ru',
                # 'Content-Length': '50',
                'Accept-Language': 'ru',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                              'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
                'Referer': 'https://rksi.ru/mobile_schedule',
                # 'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }

            group_name = urllib.parse.quote(group_name, encoding='windows-1251')
            data = f'group={group_name}&stt=%CF%EE%EA%E0%E7%E0%F2%FC%21'

            r = await session.post('https://rksi.ru/mobile_schedule', data=data, headers=headers)
            print(await r.text())

            if r.status // 100 != 2:
                raise BadResponse()

            html = await r.text()
            soup = BeautifulSoup(html, features='html.parser')
            body = soup.find('body')
            themes = []
            for i in ThemesFromPageElements(body.children).themes_generator():
                themes.append(copy.copy(i))

        return themes
