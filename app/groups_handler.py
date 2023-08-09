import asyncio
import json
import aiohttp
import more_itertools as mit

from aiohttp_socks import ProxyConnector
from app.loger_template import get_loger
from app.models.models import fill_group_table
from app.models.models import get_programs_ids
from app.common_requests import get_json
from app import engine
from config import all_connectors
from app.common_requests import process_tasks

group_logger = get_loger(__name__)
all_connectors = all_connectors[::-1]
__all__ = ['process_groups']


async def process_groups() -> None:
    """Function for processing groups"""

    async with engine.connect() as db_session:
        program_ids = await get_programs_ids(db_session)

        chunk_size = 1400
        parts = mit.chunked(program_ids, chunk_size)

        for index, part in enumerate(parts):
            connector = ProxyConnector.from_url(all_connectors[index])
            async with aiohttp.ClientSession(connector=connector) as session:
                task_list = []
                ids = []
                for item in part:
                    task_list.append(asyncio.create_task(
                        get_json(f"https://timetable.spbu.ru/api/v1/programs/{item}/groups", session)))
                    ids.append(item)
                    if len(task_list) == 30:
                        await process_tasks(task_list, ids, db_session, group_logger, process_all_groups)
                        await asyncio.sleep(0.2)
                await process_tasks(task_list, ids, db_session, group_logger, process_all_groups)
                await asyncio.sleep(0.2)


async def process_all_groups(json_string: str, program_id: int, session) -> None:
    """A function for processing groups"""
    groups_dict = json.loads(json_string)
    group_logger.info("Start of group information processing")
    group_logger.info("The beginning of filling in the Group table")
    groups = groups_dict['Groups']
    for group in groups:
        group_id = int(group["StudentGroupId"])
        name = group["StudentGroupName"]
        type_of_study = group['StudentGroupStudyForm']
        group_logger.info("The beginning of filling in the Group table")
        await fill_group_table(session, group_id, name, type_of_study, program_id)
    group_logger.info("End of filling in the Group table")
    group_logger.info("End of group information processing")

