import datetime
import asyncpg
from sqlalchemy import Column, Integer, String, text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from app.common_requests import execute

Base = declarative_base()


class Division(Base):
    """A table representing the Event entity"""
    __tablename__ = "Division"
    id = Column(Integer, primary_key=True)
    oid = Column(String(40))
    alias = Column(String(16))
    name = Column(String(70))


class Program(Base):
    """A table representing the Event entity"""
    __tablename__ = "Program"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))
    level_name = Column(String(85))
    year = Column(Integer)
    division_id = Column(Integer, ForeignKey('Division.id', ondelete='CASCADE'))


class Educator(Base):
    """A table representing the teacher entity"""
    __tablename__ = "Educator"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    middle_name = Column(String(128), nullable=True)


class Group(Base):
    """A table representing the Group entity"""
    __tablename__ = "Group"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    type = Column(String(32))
    program_id = Column(Integer, ForeignKey('Program.id', ondelete='CASCADE'))


class EducatorToEvent(Base):
    """A table for a many-to-many relationship for User and Event entities"""
    __tablename__ = "EducatorToEvent"
    educator_id = Column(Integer,
                         ForeignKey('Educator.id', ondelete='CASCADE'),
                         primary_key=True)
    # user = relationship('User', back_populates='user_events')
    event_id = Column(Integer,
                      ForeignKey('Event.id', ondelete='CASCADE'),
                      primary_key=True)


class GroupToEvent(Base):
    """A table for a many-to-many relationship for Group and Event entities"""
    __tablename__ = "GroupToEvent"
    group_id = Column(Integer,
                      ForeignKey('Group.id', ondelete='CASCADE'),
                      primary_key=True)
    event_id = Column(Integer,
                      ForeignKey('Event.id', ondelete='CASCADE'),
                      primary_key=True)


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


async def fill_group_to_event_table(session, event_id: int, group_id: int):
    await execute(
        session,
        text('INSERT INTO "GroupToEvent"(group_id, event_id)'
             'VALUES(:group_id, :event_id)'
             'ON CONFLICT(group_id, event_id) DO NOTHING'), {
            'group_id': group_id,
            'event_id': event_id
        })


async def fill_educator_to_event_table(session, event_id: int, educator_id: int):
    await execute(
        session,
        text('INSERT INTO "EducatorToEvent"(educator_id, event_id)'
             'VALUES(:educator_id, :event_id)'
             'ON CONFLICT(educator_id, event_id) DO NOTHING'), {
            'educator_id': educator_id,
            'event_id': event_id
        })


async def fill_division_table(session, oid: str, alias: str, name: str):
    """Function for filling in the Division table"""
    await execute(
        session,
        text('INSERT INTO "Division"(oid, alias, name)'
             'VALUES(:oid, :alias, :name)'
             'ON CONFLICT (id) DO NOTHING'), {
            'oid': oid,
            'alias': alias,
            'name': name
        })


async def get_division_table_dict(session):
    return {x: y for x, y in (await session.execute(text('SELECT alias, id FROM "Division"'))).fetchall()}


async def fill_program_table(session, program_id: int, name: str, level_name: str, year: int, division_id: int):
    """Function for filling in the Division table"""
    await execute(
        session,
        text('INSERT INTO "Program"(id, name, level_name, year, division_id)'
             'VALUES(:program_id, :name, :level_name, :year, :division_id)'
             'ON CONFLICT (id) DO NOTHING'), {
            'program_id': program_id,
            'name': name,
            'level_name': level_name,
            'year': year,
            'division_id': division_id
        })


async def fill_educator_table(session, user_id: int, first_name: str, last_name: str, middle_name: str) -> None:
    """Function for filling in the User table"""
    await execute(
        session,
        text(
            'INSERT INTO "Educator" (id, first_name, last_name, middle_name) '
            'VALUES(:user_id, :first_name, :last_name, :middle_name)'
            'ON CONFLICT (id) DO NOTHING;'), {
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'middle_name': middle_name,
        })


async def fill_group_table(session, group_id: int, name: str, type_of_study: str, program_id: int) -> None:
    """Function for filling in the User table"""
    await execute(
        session,
        text(
            'INSERT INTO "Group" (id, name, type, program_id) '
            'VALUES(:group_id, :name, :type_of_study, :program_id)'
            'ON CONFLICT (id) DO NOTHING;'), {
            'group_id': group_id,
            'name': name,
            'type_of_study': type_of_study,
            'program_id': program_id
        })


async def get_programs_ids(session):
    return [x[0] for x  in (await session.execute(text('SELECT id FROM "Program"'))).fetchall()]


async def get_users_ids(session):
    return [x[0] for x in (await session.execute(text('SELECT id FROM "Educator"'))).fetchall()]


async def get_group_table_dict(session):
    return {x: y for x, y in (await session.execute(text('SELECT name, id FROM "Group"'))).fetchall()}


async def delete_events(session, left_date: datetime.datetime,
                        right_date: datetime.datetime) -> None:
    await execute(session,
                  text('DELETE From "Event" '
                       'WHERE "Event".start_time >= (:left_date) '
                       'AND "Event".end_time <= (:right_date)'), {
                      'left_date': left_date,
                      'right_date': right_date
                  })


async def fill_event_table(session, dt_start: datetime.datetime,
                           dt_end: datetime.datetime, subject: str,
                           location: str) -> int:
    """Function for filling in the Event table"""
    for i in range(2):
        result = await execute(
            session,
            text(
                'WITH "ids" AS ('
                'INSERT INTO "Event" (start_time, end_time, description, location)'
                'VALUES(:start_time, :end_time, :description, :location)'
                'ON CONFLICT (start_time, end_time, description, location) '
                'DO NOTHING '
                'RETURNING id'
                ') SELECT COALESCE ('
                '(SELECT id FROM "ids"), '
                '(SELECT id FROM "Event" '
                'Where start_time=(:start_time) and end_time=(:end_time) '
                'and description=(:description) and location=(:location)));'),
            {
                'start_time': dt_start,
                'end_time': dt_end,
                'description': subject,
                'location': location
            })
        if (row := result.fetchone()) is None or (current_id := row[0]) is None:
            continue
        return current_id

    raise asyncpg.NoDataFoundError()
