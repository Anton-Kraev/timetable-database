import asyncio
import datetime
import json
import aiohttp
import asyncpg
import more_itertools as mit
import aiofiles

from aiohttp_socks import ProxyConnector
from app import (create_asyncpg_pool,
                 get_logger,
                 get_response_text,
                 delete_events,
                 fill_event_table,
                 get_educators_ids,
                 get_alias_to_id_dict,
                 fill_educator_to_event_table,
                 fill_group_to_event_table)


events_logger = get_logger(__name__)


async def events_handler(text: str,
                         connection,
                         educator_id: int,
                         groups: dict[str, int]) -> None:

    """Handler function for events json
    :param text: program json str
    :param connection: current database connection
    :param educator_id: id of the educator for whom events are being processed
    :param groups: dict of name -> id for groups"""

    dct = json.loads(text)
    educator_events_days = dct['EducatorEventsDays']

    for event in educator_events_days:
        day_study_events = event['DayStudyEvents']

        for day_event in day_study_events:
            start = day_event['Start']
            dt_start = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
            end = day_event['End']
            dt_end = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
            subject = day_event['Subject']
            location = day_event['LocationsDisplayText']
            groups_names = day_event['ContingentUnitName']
            is_cancelled = day_event['IsCancelled']

            # is_assigned = day_study_events['IsAssigned']
            # time_was_changed = day_study_events['TimeWasChanged']

            if groups_names == "Нет":
                is_cancelled = "true"
            if is_cancelled == "true":
                continue
            if (index := location.find(';')) != -1:
                location = location[:index]
            if (index := subject.find(';')) != -1:
                subject = subject[:index]
            if len(location) > 256:
                location = location[0:255]
            if len(subject) > 256:
                subject = subject[0:255]

            event_id = await fill_event_table(events_logger, connection,
                                              dt_start, dt_end,
                                              subject, location)
            await fill_educator_to_event_table(events_logger, connection,
                                               event_id, educator_id)
            split_groups_names = groups_names.split(', ')

            for group_name in split_groups_names:
                if group_name in groups:
                    group_id = groups[group_name]
                else:
                    continue
                await fill_group_to_event_table(events_logger, connection,
                                                event_id, group_id)
        # return start, end, subject, location, groups_name


async def process_tasks(task_list: list[asyncio.Task[str]],
                        connection,
                        educators_ids: list[int],
                        groups: dict[str, int]) -> None:

    """A function for starting a task and handling an exception
    :param task_list: the list of asyncio tasks for their subsequent processing
    :param connection: current database connection
    :param educators_ids:  educator ids
    :param groups: dict of name -> id for groups"""

    results = await asyncio.gather(*task_list, return_exceptions=True)
    for index, result in enumerate(results):
        if isinstance(result, BaseException):
            events_logger.error(f"{result}", exc_info=True)
            continue
        await events_handler(result, connection, educators_ids[index], groups)


async def proxy_task(connector: str,
                     part: list[int],
                     left_date: str,
                     right_date: str,
                     pool: asyncpg.Pool
                     ) -> None:
    """Handler function for each proxy
    :param connector: proxy url
    :param part: part of the educators intended
    for processing by the current proxy
    :param left_date: the left border for unloading the schedule
    :param right_date: the right border for unloading the schedule
    :param pool: asyncpg connection pool"""

    async with aiohttp.ClientSession(
            connector=ProxyConnector.from_url(connector)) as session:

        async with pool.acquire() as connection:

            groups = await get_alias_to_id_dict(connection)
            task_list = []
            items = []
            for item in part:
                task_list.append(asyncio.create_task(
                    get_response_text(
                        f"https://timetable.spbu.ru/api/v1/educators/"
                        f"{item}/events/{left_date}/{right_date}", session)))
                items.append(item)

                if len(task_list) == 30:
                    await process_tasks(task_list, connection, items, groups)
                    task_list.clear()
                    items.clear()
                    await asyncio.sleep(0.1)
            await process_tasks(task_list, connection, items, groups)


async def process_events(left_date: datetime.datetime,
                         right_date: datetime.datetime
                         ) -> None:

    """Function for event handling
    :param left_date: the left border for unloading the schedule
    :param right_date: the left border for unloading the schedule"""

    events_logger.info("Start of Event information processing")
    events_logger.info("The beginning of filling in the Event table")

    index = 0
    tasks = []
    urls = await get_events_proxy_urls()

    async with create_asyncpg_pool() as pool:
        async with pool.acquire() as connection:

            await delete_events(events_logger, connection, left_date, right_date)

            str_left_date = datetime.datetime.strftime(left_date, '%Y-%m-%d')
            str_right_date = datetime.datetime.strftime(right_date, '%Y-%m-%d')

            user_ids = await get_educators_ids(connection)
            chunk_size = 500
            parts = mit.chunked(user_ids, chunk_size)

        for index, part in enumerate(parts):
            tasks.append(asyncio.create_task(
                proxy_task(urls[index], part, str_left_date, str_right_date, pool)))
        await asyncio.gather(*tasks)

        events_logger.info("End of filling in the Event table")
        events_logger.info("End of Event information processing")

    await put_events_proxy_urls(urls, index)


async def get_events_proxy_urls() -> list[str]:
    """Function for getting http proxy"""

    urls = []
    async with aiofiles.open('events_proxies_urls', mode='r') as handle:
        async for line in handle:
            urls.append(str(line).rstrip())
    return urls


async def put_events_proxy_urls(urls: list[str], counter: int) -> None:
    """Function for adding proxy to list
    :param urls: proxy urls
    :param counter: counter of used proxies"""

    urls = urls[counter:] + urls[:counter]
    async with aiofiles.open('events_proxies_urls', mode='w') as handle:
        await handle.writelines([url + '\n' for url in urls])
