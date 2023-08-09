import asyncio
import json
import aiohttp

from aiohttp_socks import ProxyConnector
from app.models.models import fill_educator_table
from app.common_requests import get_json
from app import engine
from config import all_connectors
from app.loger_template import get_loger

user_logger = get_loger(__name__)

__all_ = ['process_all_users']


async def process_tasks(task_list: list, db_session) -> None:
    results = await asyncio.gather(*task_list, return_exceptions=True)
    task_list.clear()
    for result in results:
        if isinstance(result, aiohttp.ClientResponseError):
            user_logger.error("aiohttp.ClientResponseError", exc_info=True)
            return
        if isinstance(result, Exception):
            user_logger.error("RuntimeError", exc_info=True)
            return
        await process_all_users(result, db_session)


async def process_all_names() -> None:
    """Function for processing all variants of surnames"""

    async with engine.connect() as db_session:
        connector = ProxyConnector.from_url(all_connectors[0])
        task_list = []
        async with aiohttp.ClientSession(connector=connector) as session:
            for i in range(ord('А'), ord('Я') + 1):
                task_list.append(asyncio.create_task(
                    get_json(f"https://timetable.spbu.ru/api/v1/educators/search/{chr(i)}", session)))
                if len(task_list) == 30:
                    await process_tasks(task_list, db_session)
                    await asyncio.sleep(0.1)
            await process_tasks(task_list, db_session)
            await asyncio.sleep(0.1)


async def process_all_users(json_string: str, db_session) -> None:
    """A function for processing information about users"""

    common_dict = json.loads(json_string)
    educators = common_dict['Educators']
    user_logger.info("Start of educator information processing")
    user_logger.info("The beginning of filling in the Educator table")
    for educator in educators:
        # Пока что игнорирую post and departments
        educator_id, first_name, last_name, middle_name, employments_info = process_user(educator)
        await fill_educator_table(db_session, educator_id, first_name, last_name, middle_name)
    user_logger.info("End of filling in the Educator table")
    user_logger.info("End of user information processing")


def process_user(educator: dict) -> tuple[int, str, str, str, list] | None:
    """A function for processing information about user"""
    educator_id = educator['Id']
    full_name = educator['FullName']
    employments = educator['Employments']
    employments_info = []
    for employment in employments:
        position = employment['Position']
        department = employment['Department']
        employments_info.append((position, department))

    parts = full_name.split(' ')

    if len(parts) <= 1:
        return

    first_name = parts[0]
    last_name = parts[1]
    middle_name = None

    if len(full_name) >= 3:
        middle_name = " ".join(parts[2:])

    return educator_id, first_name, last_name, middle_name, employments_info
