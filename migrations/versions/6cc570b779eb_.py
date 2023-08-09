"""empty message

Revision ID: 6cc570b779eb
Revises: 
Create Date: 2023-07-30 22:49:21.246148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6cc570b779eb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Division',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('oid', sa.String(length=40), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Educator',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=128), nullable=True),
    sa.Column('last_name', sa.String(length=128), nullable=True),
    sa.Column('middle_name', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('location', sa.String(length=300), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('start_time', 'end_time', 'description', 'location')
    )
    op.create_table('EducatorToEvent',
    sa.Column('educator_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['educator_id'], ['Educator.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['event_id'], ['Event.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('educator_id', 'event_id')
    )
    op.create_table('Program',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=300), nullable=True),
    sa.Column('level_name', sa.String(length=85), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('division_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['division_id'], ['Division.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('type', sa.String(length=32), nullable=True),
    sa.Column('program_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['program_id'], ['Program.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('GroupToEvent',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['Event.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['group_id'], ['Group.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('group_id', 'event_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('GroupToEvent')
    op.drop_table('Group')
    op.drop_table('Program')
    op.drop_table('EducatorToEvent')
    op.drop_table('Event')
    op.drop_table('Educator')
    op.drop_table('Division')
    # ### end Alembic commands ###
