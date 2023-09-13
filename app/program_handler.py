import json
import aiohttp
import asyncio

from aiohttp_socks import ProxyConnector
from asyncpg import Pool
from config import all_connectors
from app import (get_alias_to_id_dict,
                 get_response_text,
                 process_tasks,
                 fill_program_table,
                 get_logger)

program_logger = get_logger(__name__)


async def process_programs(pool: Pool) -> None:
    """Function for processing all programs
    :param pool: asyncpg connection pool"""

    program_logger.info("Start of Program information processing")
    program_logger.info("The beginning of filling in the Program table")

    connector = ProxyConnector.from_url(all_connectors[0])

    async with aiohttp.ClientSession(connector=connector) as session:
        async with pool.acquire() as connection:

            divisions = await get_alias_to_id_dict(connection)
            task_list = []
            ids = []
            for alias, division_id in divisions.items():
                task_list.append(
                    asyncio.create_task(
                        get_response_text(
                            f"https://timetable.spbu.ru/api/v1"
                            f"/study/divisions/{alias}/programs/levels",
                            session)))
                ids.append(division_id)
                if len(task_list) == 30:
                    await process_tasks(task_list, ids, connection,
                                        program_logger, programs_handler)
                    task_list.clear()
                    ids.clear()
                    await asyncio.sleep(0.1)

            await process_tasks(task_list, ids, connection,
                                program_logger, programs_handler)

    program_logger.info("End of filling in the Program table")
    program_logger.info("End of Program information processing")


async def programs_handler(text: str, division_id: int, connection) -> None:
    """Handler function for program json
    :param text: program json str
    :param division_id: program id
    :param connection: current database connection"""

    program_dct = json.loads(text)
    for study_level in program_dct:
        level_name = study_level['StudyLevelNameEnglish']
        programs_for_study_level = study_level['StudyProgramCombinations']
        for program in programs_for_study_level:
            program_name = program['NameEnglish']
            for admissionYear in program['AdmissionYears']:
                study_program_id = int(admissionYear['StudyProgramId'])
                year_number = int(admissionYear['YearNumber'])
                await fill_program_table(program_logger, connection,
                                         study_program_id, program_name,
                                         level_name, year_number, division_id)
