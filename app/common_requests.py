import aiohttp
import asyncio
import typing as tp
import asyncpg
import logging

from sqlalchemy.ext.asyncio import AsyncConnection


async def get_json(url: str, session: aiohttp.ClientSession) -> str:
    """Function for getting result of get requests"""
    delay = 1
    for i in range(4):
        async with session.get(url=url) as resp:
            if resp.ok:
                return await resp.text()
            await asyncio.sleep(delay)
            delay *= 2
    async with session.get(url=url) as resp:
        if resp.ok:
            return await resp.text()
    resp.raise_for_status()
    return ""


async def execute(session: AsyncConnection, txt, dct: dict[str, tp.Any]):
    """A function for performing a database operation"""
    try:
        result = await session.execute(txt, dct)
    except asyncpg.IntegrityConstraintViolationError:
        logging.error("asyncpg.IntegrityConstraintViolationError", exc_info=True)
        return
    else:
        logging.info("Success insert into table")
        await session.commit()
    return result


async def process_tasks(task_list: list, indexes: list[int],  db_session, logger, func) -> None:
    """A function for starting a task and handling an exception"""
    results = await asyncio.gather(*task_list, return_exceptions=True)
    task_list.clear()
    new_idxs = []
    for index, result in enumerate(results):
        if isinstance(result, aiohttp.ClientResponseError):
            logger.error(f"{result}", exc_info=True)
            task_list.append(result)
            new_idxs.append(indexes[index])
            continue
        if isinstance(result, Exception):
            logger.error(f"{result}", exc_info=True)
            return
        await func(result, indexes[index], db_session)
    indexes.clear()
    if len(task_list) > 0:
        await process_tasks(task_list, new_idxs, db_session, logger, func)
