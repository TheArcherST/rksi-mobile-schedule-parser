import asyncio

from fastapi import FastAPI
from pydantic import BaseModel

from parser.rksi import RKSIScheduleParser


app = FastAPI()


@app.get('/schedule/{group}')
async def get_today_schedule(group: str):
    return


async def main():
    parser = RKSIScheduleParser()

    if not await parser.is_alive():
        return print('Not alive')

    themes = await parser.parse_group_themes('ИБА-21')
    current_date = None

    for i in themes:
        if current_date != i.date:
            current_date = i.date
            print('=' * 20)
            print(i.date.strftime('%d.%m'))
        else:
            current_date = i.date
        print(i.starts_at.strftime('%H:%M'), '-', i.ends_at.strftime('%H:%M'), i.name, f'({i.teacher})')


if __name__ == '__main__':
    asyncio.run(main())
