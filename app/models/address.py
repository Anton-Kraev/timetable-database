import logging

from . import Base, Column, Integer, String, execute


class Address(Base):
    """A table representing the Address entity"""

    __tablename__ = "Address"
    id = Column(Integer, primary_key=True)
    oid = Column(String(40), unique=True)
    name = Column(String(70))
    matches = Column(Integer)


async def fill_address_table(logger: logging.Logger, connection, oid: str, name: str, matches: int) -> None:
    """Function for filling in the Address table
    :param logger: logger for Address handler
    :param connection: current database connection
    :param oid: address oid
    :param name: address name
    :param matches: matches"""

    await execute(logger, connection,
                  """INSERT INTO "Address"(oid, name, matches)
                   VALUES($1, $2, $3)
                   ON CONFLICT (oid) DO NOTHING;""",
                  [(oid, name, matches)])


async def get_addresses_oid_to_id_dict(connection) -> dict[str, int]:
    """Function for getting addresses oid -> id dict
    :param param connection: current database connection"""

    return {record['oid']: record['id'] for record in
            (await connection.fetch("""SELECT Oid, id FROM "Address";"""))}
