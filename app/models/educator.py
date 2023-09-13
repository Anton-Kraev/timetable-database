from logging import Logger
from . import Base, Column, Integer, String, execute


class Educator(Base):
    """A table representing the Educator entity"""

    __tablename__ = "Educator"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    middle_name = Column(String(128), nullable=True)


async def fill_educator_table(logger: Logger, connection,
                              educator_id: int, first_name: str,
                              last_name: str, middle_name: str) -> None:
    """Function for filling in the Educator table
    :param logger: logger for Educator handler
    :param connection: current database connection
    :param educator_id: educator id
    :param first_name: first name
    :param last_name: last name
    :param middle_name: middle name"""

    await execute(logger, connection,
                  """INSERT INTO "Educator" (id, first_name, last_name, middle_name)
                  VALUES($1, $2, $3, $4)
                  ON CONFLICT (id) DO NOTHING;""",
                  [(educator_id, first_name, last_name, middle_name)])


async def get_educators_ids(connection) -> list[int]:
    """Function for getting educators ids list
    :param param connection: current database connection"""

    return [record['id'] for record in
            (await connection.fetch("""SELECT id FROM "Educator";"""))]
