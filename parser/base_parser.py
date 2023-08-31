from .models import ThemeSource


class ParsingError(Exception):
    pass


class BadResponse(ParsingError):
    ...


class BaseScheduleParser:
    def __init__(self, *args, **kwargs):
        pass

    async def is_alive(self) -> bool:
        pass

    async def parse_group_themes(self, identifier: str) -> list[ThemeSource]:
        pass
