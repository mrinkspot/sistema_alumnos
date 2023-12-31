"""materias y cursadas 2

Revision ID: 89458c05c803
Revises: cd9f40bd3bb7
Create Date: 2023-06-29 14:42:58.130187

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89458c05c803'
down_revision = 'cd9f40bd3bb7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Materias',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('descripcion', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Cursadas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('alumno_padron', sa.Integer(), nullable=False),
    sa.Column('materia_id', sa.Integer(), nullable=False),
    sa.Column('nota', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['alumno_padron'], ['Alumnos.padron'], ),
    sa.ForeignKeyConstraint(['materia_id'], ['Materias.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Cursadas')
    op.drop_table('Materias')
    # ### end Alembic commands ###
