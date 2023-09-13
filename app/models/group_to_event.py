from logging import Logger
from . import Base, Column, Integer, ForeignKey, execute


class GroupToEvent(Base):
    """A table for a many-to-many relationship for Group and Event entities"""

    __tablename__ = "GroupToEvent"
    group_id = Column(Integer,
                      ForeignKey('Group.id', ondelete='CASCADE'),
                      primary_key=True)
    event_id = Column(Integer,
                      ForeignKey('Event.id', ondelete='CASCADE'),
                      primary_key=True)


async def fill_group_to_event_table(logger: Logger, connection,
                                    event_id: int, group_id: int
                                    ) -> None:
    """Function for filling in the GroupToEvent table
    :param logger: logger for GroupToEvent handler
    :param connection: current database connection
    :param event_id: event_id
    :param group_id: group_id"""

    await execute(logger, connection,
                  """INSERT INTO "GroupToEvent"(group_id, event_id)
                  VALUES($1, $2)
                  ON CONFLICT(group_id, event_id) DO NOTHING""",
                  [(group_id, event_id)])
