import asyncio
import json
import aiohttp
import more_itertools as mit

from aiohttp_socks import ProxyConnector
from asyncpg import Pool
from config import all_connectors
from app import (get_logger,
                 fill_group_table,
                 get_programs_ids,
                 get_response_text,
                 process_tasks)

group_logger = get_logger(__name__)
all_connectors = all_connectors[::-1]


async def proxy_task(connector: ProxyConnector,
                     pool: Pool,
                     part: list[int]
                     ) -> None:
    """Handler function for each proxy
    :param connector: proxy connector
    :param pool: asyncpg connection pool
    :param part: part of the groups intended
    for processing by the current proxy
    """

    task_list = []
    ids = []

    async with aiohttp.ClientSession(connector=connector) as session:
        async with pool.acquire() as connection:
            for item in part:
                task_list.append(asyncio.create_task(
                    get_response_text(
                        f"https://timetable.spbu.ru/api/v1/programs"
                        f"/{item}/groups", session)))
                ids.append(item)

                if len(task_list) == 30:
                    await process_tasks(task_list, ids, connection,
                                        group_logger, process_all_groups)
                    task_list.clear()
                    ids.clear()
                    await asyncio.sleep(0.1)

            await process_tasks(task_list, ids, connection,
                                group_logger, process_all_groups)


async def process_groups(pool: Pool) -> None:
    """Function for processing groups
    :param pool: asyncpg connection pool"""

    group_logger.info("Start of Group information processing")
    group_logger.info("The beginning of filling in the Group table")

    async with pool.acquire() as connection:
        programs_ids = await get_programs_ids(connection)

    chunk_size = 1400
    parts = mit.chunked(programs_ids, chunk_size)
    tasks = []

    for index, part in enumerate(parts):
        connector = ProxyConnector.from_url(all_connectors[index])
        tasks.append(asyncio.create_task(
            proxy_task(connector, pool, part)))

    await asyncio.gather(*tasks)

    group_logger.info("End of filling in the Group table")
    group_logger.info("End of Group information processing")


async def process_all_groups(text: str, program_id: int, connection) -> None:
    """A function for processing groups
    :param text: groups json str
    :param program_id: program id
    :param connection: current database connection"""

    groups_dict = json.loads(text)
    groups = groups_dict['Groups']
    for group in groups:
        group_id = int(group["StudentGroupId"])
        name = group["StudentGroupName"]
        type_of_study = group['StudentGroupStudyForm']
        group_logger.info("The beginning of filling in the Group table")
        await fill_group_table(group_logger, connection, group_id,
                               name, type_of_study, program_id)
