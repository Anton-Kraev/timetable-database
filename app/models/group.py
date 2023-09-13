from logging import Logger
from . import Base, Column, Integer, String, ForeignKey, execute


class Group(Base):
    """A table representing the Group entity"""

    __tablename__ = "Group"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    type = Column(String(32))
    program_id = Column(Integer, ForeignKey('Program.id', ondelete='CASCADE'))


async def fill_group_table(logger: Logger, connection,
                           group_id: int, name: str,
                           type_of_study: str, program_id: int
                           ) -> None:
    """Function for filling in the Group table
    :param logger: logger for Group handler
    :param connection: current database connection
    :param group_id: group id
    :param name: group name
    :param type_of_study: type_of_study
    :param program_id: program id for program"""

    await execute(logger, connection,
                  """INSERT INTO "Group" (id, name, type, program_id)
                  VALUES($1, $2, $3, $4)
                  ON CONFLICT (id) DO NOTHING;""",
                  [(group_id, name, type_of_study, program_id)])


async def get_group_table_dict(connection) -> dict[str, int]:
    """Function for getting name -> id dictionary
    :param param connection: current database connection"""

    return {record['name']: record['id'] for record in
            (await connection.fetch("""SELECT name, id FROM "Group";"""))}
