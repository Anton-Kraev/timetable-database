from logging import Logger
from . import Base, Column, Integer, ForeignKey, execute


class EducatorToEvent(Base):
    """A table for a many-to-many relationship
     for Educator and Event entities"""

    __tablename__ = "EducatorToEvent"
    educator_id = Column(Integer,
                         ForeignKey('Educator.id', ondelete='CASCADE'),
                         primary_key=True)
    # user = relationship('User', back_populates='user_events')
    event_id = Column(Integer,
                      ForeignKey('Event.id', ondelete='CASCADE'),
                      primary_key=True)


async def fill_educator_to_event_table(logger: Logger, connection,
                                       event_id: int, educator_id: int
                                       ) -> None:
    """Function for filling in the EducatorToEvent table
    :param logger: logger for EducatorToEvent handler
    :param connection: current database connection
    :param event_id: event_id
    :param educator_id: educator_id"""

    await execute(logger, connection,
                  """INSERT INTO "EducatorToEvent"(educator_id, event_id)
                  VALUES($1, $2)
                  ON CONFLICT(educator_id, event_id) DO NOTHING""",
                  [(educator_id, event_id)])
