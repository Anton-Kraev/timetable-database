import asyncpg

from config import user, password, name, host
from app.models.division import fill_division_table, get_alias_to_id_dict
from app.common_requests import get_response_text, process_tasks, execute
from app.logger_template import get_logger
from app.models.group import fill_group_table
from app.models.program import get_programs_ids, fill_program_table
from app.models.educator import fill_educator_table, get_educators_ids
from app.models.event import delete_events, fill_event_table
from app.models.educator_to_event import fill_educator_to_event_table
from app.models.group_to_event import fill_group_to_event_table
from app.models.address import fill_address_table, get_addresses_oid_to_id_dict
from app.models.classroom import fill_classroom_table


def create_asyncpg_pool():
    return asyncpg.create_pool(user=user, password=password,
                               database=name, host=host)
