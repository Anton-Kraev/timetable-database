import json
import aiohttp

from aiohttp_socks import ProxyConnector
from config import all_connectors
from asyncpg import Pool
from app import (fill_address_table,
                 get_response_text,
                 get_logger)

addresses_logger = get_logger(__name__)


async def process_addresses(pool: Pool) -> None:
    """Function for processing all addresses
    :param pool: asyncpg connection pool"""

    addresses_url = "https://timetable.spbu.ru/api/v1/addresses"
    connector = ProxyConnector.from_url(all_connectors[0])

    async with aiohttp.ClientSession(connector=connector) as session:
        response_json = await get_response_text(addresses_url, session)
        division_json = json.loads(response_json)

        addresses_logger.info("Start of Addresses information processing")
        addresses_logger.info("The beginning of filling in the Addresses table")

        async with pool.acquire() as connection:
            for element in division_json:
                oid = element['Oid']
                name = element['DisplayName1']
                matches = element['matches']
                await fill_address_table(addresses_logger, connection,
                                         oid, name, matches)

        addresses_logger.info("End of filling in the Addresses table")
        addresses_logger.info("End of Addresses information processing")
