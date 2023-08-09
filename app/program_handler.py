import json
import aiohttp
import asyncio

from aiosocksy.connector import ProxyConnector
from aiohttp_socks import ProxyConnector
from app.models.models import get_division_table_dict
from app.common_requests import get_json
from app.models.models import fill_program_table
from app import engine
from config import all_connectors
from app.loger_template import get_loger
from app.common_requests import process_tasks

program_logger = get_loger(__name__)


async def process_programs() -> None:
    """Function for processing all programs"""
    task_list = []
    connector = ProxyConnector.from_url(all_connectors[0])
    async with aiohttp.ClientSession(connector=connector) as session:
        async with engine.connect() as db_session:
            divisions = await get_division_table_dict(db_session)
            ids = []
            for alias, division_id in divisions.items():
                task_list.append(
                    asyncio.create_task(get_json(f"https://timetable.spbu.ru/api/v1/study/divisions/{alias}/programs/levels", session)))
                ids.append(division_id)
                if len(task_list) == 30:
                    await process_tasks(task_list, ids, db_session, program_logger, process_all_programs)
                    await asyncio.sleep(0.1)
            await process_tasks(task_list, ids, db_session, program_logger, process_all_programs)
            await asyncio.sleep(0.1)


async def process_all_programs(text: str, division_id: int, db_session) -> None:
    program_dct = json.loads(text)
    program_logger.info("Start of Program information processing")
    program_logger.info("The beginning of filling in the Program table")
    for study_level in program_dct:
        level_name = study_level['StudyLevelNameEnglish']
        programs_for_study_level = study_level['StudyProgramCombinations']
        for program in programs_for_study_level:
            program_name = program['NameEnglish']
            for admissionYear in program['AdmissionYears']:
                study_program_id = int(admissionYear['StudyProgramId'])
                year_number = int(admissionYear['YearNumber'])
                await fill_program_table(db_session, study_program_id, program_name, level_name, year_number, division_id)
    program_logger.info("End of filling in the Program table")
    program_logger.info("End of Program information processing")
