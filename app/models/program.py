from logging import Logger
from . import Base, Column, Integer, String, ForeignKey, execute


class Program(Base):
    """A table representing the Program entity"""

    __tablename__ = "Program"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))
    level_name = Column(String(85))
    year = Column(Integer)
    division_id = Column(Integer,
                         ForeignKey('Division.id', ondelete='CASCADE'))


async def fill_program_table(logger: Logger, connection,
                             program_id: int, name: str,
                             level_name: str, year: int,
                             division_id: int) -> None:
    """Function for filling in the Program table
    :param logger: logger for program handler
    :param connection: current database connection
    :param program_id: program id
    :param name: program name
    :param level_name: level_name for program
    :param year: year
    :param division_id: division id for program"""

    await execute(logger, connection,
                  """INSERT INTO "Program" (id, name, level_name, year, division_id)
                   VALUES($1, $2, $3, $4, $5)
                   ON CONFLICT (id) DO NOTHING;""",
                  [(program_id, name, level_name, year, division_id)])


async def get_programs_ids(connection) -> list[int]:
    """Function for getting program ids list
    :param param connection: current database connection"""

    return [record['id'] for record in
            (await connection.fetch("""SELECT id FROM "Program";"""))]
