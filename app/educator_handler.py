import asyncio
import json
import aiohttp
import typing as tp

from aiohttp_socks import ProxyConnector
from asyncpg import Pool
from config import all_connectors
from app import (fill_educator_table,
                 get_response_text,
                 get_logger)

educator_logger = get_logger(__name__)


async def process_educators_tasks(task_list: list[asyncio.Task[str]],
                                  connection: tp.Any) -> None:
    """A function for starting a task and handling an exception
    :param task_list: the list of asyncio tasks for their subsequent processing
    :param connection: current database connection"""

    results = await asyncio.gather(*task_list, return_exceptions=True)
    for result in results:
        if isinstance(result, BaseException):
            educator_logger.error(f"{result}", exc_info=True)
            return
        await process_all_educators(result, connection)


async def process_all_names(pool: Pool) -> None:
    """Function for processing all variants of surnames
    :param pool: asyncpg connection pool"""

    educator_logger.info("Start of Educator information processing")
    educator_logger.info("The beginning of filling in the Educator table")

    user_url = "https://timetable.spbu.ru/api/v1/educators/search/"
    connector = ProxyConnector.from_url(all_connectors[0])
    task_list = []

    async with pool.acquire() as connection:
        async with aiohttp.ClientSession(connector=connector) as session:

            for i in range(ord('А'), ord('Я') + 1):
                task_list.append(
                    asyncio.create_task(
                        get_response_text(user_url + chr(i), session)))
                if len(task_list) == 30:
                    await process_educators_tasks(task_list, connection)
                    task_list.clear()
                    await asyncio.sleep(0.1)

            await process_educators_tasks(task_list, connection)
            await asyncio.sleep(0.1)

    educator_logger.info("End of filling in the Educator table")
    educator_logger.info("End of Educator information processing")


async def process_all_educators(text: str, connection: tp.Any) -> None:
    """Handler function for program json
    :param text: program json str
    :param connection: current database connection"""

    common_dict = json.loads(text)
    if common_dict is None:
        return

    educators = common_dict['Educators']

    if educators is None:
        return

    for educator in educators:
        # Пока что игнорирую post and departments
        if (result := process_user(educator)) is None:
            return
        (educator_id, first_name, last_name,
         middle_name, employments_info) = result

        await fill_educator_table(educator_logger, connection, educator_id,
                                  first_name, last_name, middle_name)


def process_user(educator: dict) \
        -> tuple[int, str, str, str | None, list[tuple[str, str]]] | None:
    """A function for processing information about user"""

    educator_id: int = educator['Id']
    full_name: str = educator['FullName']
    employments = educator['Employments']
    employments_info = []

    for employment in employments:
        position: str = employment['Position']
        department: str = employment['Department']
        employments_info.append((position, department))

    parts = full_name.split(' ')

    if len(parts) <= 1:
        return None

    first_name: str = parts[0]
    last_name: str = parts[1]
    middle_name = None

    if len(full_name) >= 3:
        middle_name = " ".join(parts[2:])

    return educator_id, first_name, last_name, middle_name, employments_info
