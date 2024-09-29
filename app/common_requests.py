import aiohttp
import asyncio
import logging
import typing as tp

from tenacity import retry, wait_exponential, stop_after_attempt
from asyncpg import IntegrityConstraintViolationError


@retry(wait=wait_exponential(multiplier=1, min=1, max=4), stop=stop_after_attempt(5))
async def get_response_text(url: str, session: aiohttp.ClientSession) -> str:
    """Function for getting result of get requests
    :param url: str for aiohttp response
    :param session: current aiohttp.ClientSession
    :return: response text
    """

    async with session.get(url=url, raise_for_status=True) as resp:
        return await resp.text()


async def execute(logger: logging.Logger,
                  connection, txt,
                  args: list[tuple[tp.Any, ...]]) -> None:
    """A function for performing a database operation
    :param logger: logger of the calling module
    :param connection: current database session
    :param txt: request text
    :param args: request arguments"""

    try:
        async with connection.transaction():
            await connection.executemany(txt, args)
    except IntegrityConstraintViolationError:
        logger.error("asyncpg.IntegrityConstraintViolationError",
                     exc_info=True)
        return


async def process_tasks(task_list: list[asyncio.Task[str]],
                        indexes: list[int],
                        connection: tp.Any,
                        logger: logging.Logger,
                        func: tp.Callable[...,
                        tp.Coroutine[tp.Any, tp.Any, None]]
                        ) -> None:

    """A function for starting a task and handling an exception
    :param task_list: the list of asyncio tasks for their subsequent processing
    :param indexes: a list of indexes corresponding to each task
    :param connection: current database session
    :param logger: logger for the module from which the function is called
    :param func: callable for subsequent processing of values received
    after asyncio tasks await"""

    results = await asyncio.gather(*task_list, return_exceptions=True)
    for index, result in enumerate(results):
        if isinstance(result, BaseException):
            logger.error(f"{result}", exc_info=True)
            continue
        await func(result, indexes[index], connection)
