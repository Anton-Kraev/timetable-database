import json
import aiohttp
import asyncio

from aiohttp_socks import ProxyConnector
from asyncpg import Pool
from config import all_connectors
from app import (get_addresses_oid_to_id_dict,
                 get_logger, get_response_text,
                 process_tasks, fill_classroom_table)

classroom_logger = get_logger(__name__)


async def process_classrooms(pool: Pool) -> None:
    """Function for processing all classrooms
    :param pool: asyncpg connection pool"""

    classroom_logger.info("Start of Classrooms information processing")
    classroom_logger.info("The beginning of filling in the Classrooms table")

    connector = ProxyConnector.from_url(all_connectors[0])

    async with aiohttp.ClientSession(connector=connector) as session:
        async with pool.acquire() as connection:

            addresses = await get_addresses_oid_to_id_dict(connection)
            task_list = []
            ids = []
            for address_oid, address_id in addresses.items():
                task_list.append(
                    asyncio.create_task(
                        get_response_text(f"https://timetable.spbu.ru/api"
                                          f"/v1/addresses/{address_oid}/classrooms",
                                          session)))
                ids.append(address_id)
                if len(task_list) == 30:
                    await process_tasks(task_list, ids, connection,
                                        classroom_logger, classroom_handler)
                    task_list.clear()
                    ids.clear()
                    await asyncio.sleep(0.1)

            await process_tasks(task_list, ids, connection,
                                classroom_logger, classroom_handler)

    classroom_logger.info("End of filling in the Classroom table")
    classroom_logger.info("End of Classroom information processing")


async def classroom_handler(text: str, address_id: int, connection) -> None:
    """Handler function for classroom json
    :param text: classroom json str
    :param address_id: address id
    :param connection: current database connection"""

    classroom_dct = json.loads(text)
    for classroom in classroom_dct:
        oid = classroom['Oid']
        name = classroom['DisplayName1']
        seating_type = int(classroom['SeatingType'])
        capacity = int(classroom['Capacity'])
        additional_info = classroom['AdditionalInfo']
        await fill_classroom_table(classroom_logger, connection, oid,
                                   name, capacity, seating_type,
                                   additional_info, address_id)
