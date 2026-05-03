"""initial

Revision ID: c6c4b787c863
Revises:
Create Date: 2026-05-03 14:36:20.990325

"""

from typing import Sequence, Union

from alembic import op
from src.utils.import_util import get_models_metadata

# revision identifiers, used by Alembic.
revision: str = "c6c4b787c863"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    metadata = get_models_metadata()
    for table in metadata.tables.values():
        table.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Downgrade schema."""
    metadata = get_models_metadata()
    for table in reversed(metadata.tables.values()):
        table.drop(op.get_bind(), checkfirst=True)
