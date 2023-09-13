import datetime
import asyncpg

from logging import Logger
from . import (Base, Column, Integer,
               String, DateTime,
               UniqueConstraint, execute)


class Event(Base):
    """A table representing the Event entity"""

    __tablename__ = "Event"
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    description = Column(String(256))
    location = Column(String(256))
    __table_args__ = (UniqueConstraint('start_time', 'end_time', 'description',
                                       'location'),)


async def fill_event_table(logger: Logger, connection,
                           dt_start: datetime.datetime,
                           dt_end: datetime.datetime,
                           subject: str, location: str) -> int:
    """Function for filling in the Event table
    :param logger: logger for Event handler
    :param connection: current database connection
    :param dt_start: the left time boundary of the event
    :param dt_end: the right time boundary of the event
    :param subject: subject
    :param location: location"""

    query = """WITH "ids" AS (
INSERT INTO "Event" (start_time, end_time, description, location)
VALUES($1, $2, $3, $4)
ON CONFLICT (start_time, end_time, description, location)
DO NOTHING
RETURNING id
) SELECT COALESCE (
(SELECT id FROM "ids"),
(SELECT id FROM "Event"
Where start_time=($1) and end_time=($2)
and description=($3) and location=($4)));"""

    for i in range(2):
        result = await connection.fetchrow(logger, connection, query,
                                           [(dt_start, dt_end, subject, location)])
        if result is None or (current_id := result['id']) is None:
            continue
        return current_id

    raise asyncpg.NoDataFoundError()


async def delete_events(logger: Logger, connection,
                        left_date: datetime.datetime,
                        right_date: datetime.datetime) -> None:
    """Function for deleting event in the Event table
    :param logger: logger for Event handler
    :param connection: current database connection
    :param left_date: the left time boundary for deleting events
    :param right_date: the right time boundary for deleting events"""

    await execute(logger, connection,
                  """DELETE From "Event"
                  WHERE "Event".start_time >= ($1)
                  AND "Event".end_time <= ($2);""",
                  [(left_date, right_date)])
