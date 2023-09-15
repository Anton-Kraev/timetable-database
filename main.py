import asyncio
import sys

from datetime import datetime, timedelta, time
from app.division_handler import process_divisions
from app.program_handler import process_programs
from app.groups_handler import process_groups
from app.events_handler import process_events
from app.educator_handler import process_all_names
from app.address_handler import process_addresses
from app import create_asyncpg_pool


async def fill_users() -> None:
    async with create_asyncpg_pool() as pool:
        await process_addresses(pool)
        await process_divisions(pool)
        await process_programs(pool)
        await process_all_names(pool)
        await process_groups(pool)


async def fill_events():
    # start = datetime(year=2023, month=8, day=1)
    now = datetime.combine(datetime.now(), time.min)
    await process_events(now, now + timedelta(days=28))


if __name__ == '__main__':
    if sys.argv[1] == "users":
        asyncio.run(fill_users())
    elif sys.argv[1] == "events":
        asyncio.run(fill_events())
