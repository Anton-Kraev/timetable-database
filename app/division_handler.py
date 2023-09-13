import json
import aiohttp

from aiohttp_socks import ProxyConnector
from config import all_connectors
from asyncpg import Pool
from app import (fill_division_table,
                 get_response_text,
                 get_logger)

division_logger = get_logger(__name__)


async def process_divisions(pool: Pool) -> None:
    """Function for processing all divisions
    :param pool: asyncpg connection pool"""

    divisions_url = "https://timetable.spbu.ru/api/v1/study/divisions"
    connector = ProxyConnector.from_url(all_connectors[0])

    async with aiohttp.ClientSession(connector=connector) as session:
        response_json = await get_response_text(divisions_url, session)
        division_json = json.loads(response_json)

        division_logger.info("Start of Division information processing")
        division_logger.info("The beginning of filling in the Division table")

        async with pool.acquire() as connection:
            for element in division_json:
                oid = element['Oid']
                alias = element['Alias']
                name = element['Name']
                await fill_division_table(division_logger, connection,
                                          oid, alias, name)

        division_logger.info("End of filling in the Division table")
        division_logger.info("End of Division information processing")
