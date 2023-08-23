import asyncio
import concurrent.futures
import datetime
import json
import aiohttp
import more_itertools as mit
import aiofiles

from aiohttp_socks import ProxyConnector
from app import engine
from app.loger_template import get_loger
from app.models.models import delete_events, \
    fill_event_table, \
    get_users_ids, \
    get_group_table_dict, fill_educator_to_event_table, fill_group_to_event_table
from app.common_requests import get_json


events_logger = get_loger(__name__)


async def events_handler(text, db_session, user_id: int, groups) -> None:
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
            event_id = await fill_event_table(db_session, dt_start, dt_end, subject, location)
            await fill_educator_to_event_table(db_session, event_id, user_id)
            split_groups_names = groups_names.split(', ')
            for group_name in split_groups_names:
                if group_name in groups:
                    group_id = groups[group_name]
                else:
                    continue
                await fill_group_to_event_table(db_session, event_id, group_id)
        # return start, end, subject, location, groups_name


async def process_tasks(task_list: list, db_session, user_ids: list[int], groups) -> None:
    """A function for starting a task and handling an exception"""
    results = await asyncio.gather(*task_list, return_exceptions=True)
    task_list.clear()
    new_user_ids = []
    for index, result in enumerate(results):
        if isinstance(result, Exception):
            events_logger.error(f"{result}", exc_info=True)
            continue
        await events_handler(result, db_session, user_ids[index], groups)
    user_ids.clear()


async def proxy_handler(connector, part, groups, left_date, right_date) -> None:
    async with engine.connect() as db_session:
        async with aiohttp.ClientSession(connector=ProxyConnector.from_url(connector)) as session:
            task_list = []
            items = []
            for item in part:
                task_list.append(asyncio.create_task(
                    get_json(f"https://timetable.spbu.ru/api/v1/educators/{item}/events/{left_date}/{right_date}",
                             session)))
                items.append(item)
                if len(task_list) == 30:
                    await process_tasks(task_list, db_session, items, groups)
                    await asyncio.sleep(0.1)
            await process_tasks(task_list, db_session, items, groups)
            await asyncio.sleep(0.1)


def asyncio_starter(connector, part, groups, left_date, right_date) -> None:
    asyncio.run(proxy_handler(connector, part, groups, left_date, right_date))


async def process_events(left_date: str, right_date: str, urls, user_row, groups) -> int:
    """Function for event handling"""
    chunk_size = 500
    parts = mit.chunked(user_row, chunk_size)
    index = 0
    for index, part in enumerate(parts):
        await proxy_handler(urls[index], part, groups, left_date, right_date)
    return index


async def get_events_proxy_urls() -> list[str]:
    """Function for getting http proxy"""
    urls = []
    async with aiofiles.open('events_proxies_urls', mode='r') as handle:
        async for line in handle:
            urls.append(str(line).rstrip())
    return urls


async def get_user_and_group_rows(left_date: datetime.datetime, right_date: datetime.datetime) -> (list[int], dict[str, int]):
    """Function for getting all user and group ids"""
    async with engine.connect() as db_session:
        await delete_events(db_session, left_date, right_date)
        user_row = await get_users_ids(db_session)
        groups = await get_group_table_dict(db_session)
    await engine.dispose()
    return user_row, groups


async def put_events_proxy_urls(urls: list[str], counter: int) -> None:
    """Function for adding proxy to list"""
    urls = urls[counter:] + urls[:counter]
    async with aiofiles.open('events_proxies_urls', mode='w') as handle:
        await handle.writelines([url + '\n' for url in urls])
