import logging

from . import Base, Column, Integer, String, ForeignKey, execute


class Classroom(Base):
    """A table representing the Classroom entity"""

    __tablename__ = "Classroom"
    id = Column(Integer, primary_key=True)
    oid = Column(String(40), unique=True)
    name = Column(String(100))
    capacity = Column(Integer)
    seating_type = Column(Integer)
    additional_info = Column(String())
    address_id = Column(Integer,
                        ForeignKey('Address.id', ondelete='CASCADE'))


async def fill_classroom_table(logger: logging.Logger, connection, oid: str,
                               name: str, capacity: int, seating_type: int,
                               additional_info: str, address_id: int) -> None:
    """Function for filling in the Classroom table
    :param logger: logger for classroom handler
    :param connection: current database connection
    :param oid: classroom oid
    :param name: classroom name
    :param seating_type: seating type
    :param capacity: classroom capacity
    :param additional_info: classroom additional info
    :param address_id: address id"""
    additional_info = additional_info and additional_info[:300]

    await execute(logger, connection,
                  """INSERT INTO "Classroom"(oid, name, capacity, seating_type, additional_info, address_id)
                   VALUES($1, $2, $3, $4, $5,$6)
                   ON CONFLICT (oid) DO NOTHING;""",
                  [(oid, name, capacity, seating_type, additional_info, address_id)])
