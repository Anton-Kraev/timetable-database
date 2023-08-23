import asyncio
import datetime
import sys
import more_itertools as mit
import aiofiles
import pandas as pd
import sentry_sdk
from app.division_handler import process_divisions
from app.program_handler import process_programs
from app.groups_handler import process_groups
from app.events_handler import process_events
from app.user_handler import process_all_names
from app.events_handler import get_events_proxy_urls, get_user_and_group_rows, put_events_proxy_urls, delete_events


async def fill_users() -> None:
    await process_divisions()
    await process_programs()
    await process_all_names()
    await process_groups()


async def fill_events():
    now = datetime.datetime.today()
    snd_date = now + datetime.timedelta(days=28)
    urls = await get_events_proxy_urls()
    user_row, groups = await get_user_and_group_rows(now, snd_date)
    counter = await process_events(f"{now.year}-{now.month}-{now.day}", f"{snd_date.year}-{snd_date.month}-{snd_date.day}",
                             urls, user_row, groups)
    await put_events_proxy_urls(urls, counter)


if __name__ == '__main__':
    sentry_sdk.init(
        dsn="https://ba2ef865354a9932dbe945a058bb50cf@o4505702880641024.ingest.sentry.io/4505702896173056",
        traces_sample_rate=0.85)
    if sys.argv[1] == "users":
        asyncio.run(fill_users())
    elif sys.argv[1] == "events":
        asyncio.run(fill_events())
