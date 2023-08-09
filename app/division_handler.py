import json
import aiohttp
from aiohttp_socks import ProxyConnector

from app.models.models import fill_division_table
from app.common_requests import get_json
from app.loger_template import get_loger
from app import engine
from config import all_connectors

division_loger = get_loger(__name__)


async def process_divisions() -> None:
    """Function for processing all divisions"""
    connector = ProxyConnector.from_url(all_connectors[0])
    async with aiohttp.ClientSession(connector=connector) as session:
        text = await get_json("https://timetable.spbu.ru/api/v1/study/divisions", session)
        division_dct = json.loads(text)
        division_loger.info("Start of division information processing")
        division_loger.info("The beginning of filling in the Division table")
        async with engine.connect() as db_session:
            for element in division_dct:
                oid = element['Oid']
                alias = element['Alias']
                name = element['Name']
                await fill_division_table(db_session, oid, alias, name)
        division_loger.info("End of filling in the Group table")
        division_loger.info("End of division information processing")
