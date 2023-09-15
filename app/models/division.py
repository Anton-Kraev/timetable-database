from logging import Logger
from . import Base, Column, Integer, String, execute


class Division(Base):
    """A table representing the Division entity"""

    __tablename__ = "Division"
    id = Column(Integer, primary_key=True)
    oid = Column(String(40), unique=True)
    alias = Column(String(16))
    name = Column(String(70))


async def fill_division_table(logger: Logger, connection,
                              oid: str, alias: str, name: str) -> None:
    """Function for filling in the Division table
    :param logger: logger for Division handler
    :param connection: current database connection
    :param oid: division oid
    :param alias: division alias
    :param name: division name"""

    await execute(logger, connection,
                  """INSERT INTO "Division"(oid, alias, name)
                   VALUES($1, $2, $3)
                   ON CONFLICT (oid) DO NOTHING;""",
                  [(oid, alias, name)])


async def get_alias_to_id_dict(connection) -> dict[str, int]:
    """Function for getting alias -> id dictionary
    :param param connection: current database connection"""

    return {record['alias']: record['id'] for record in
            (await connection.fetch("""SELECT alias, id FROM "Division";"""))}
