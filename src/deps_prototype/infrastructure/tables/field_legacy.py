from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB

from deps_prototype.extras.datasource import metadata

__all__ = ["field_table"]

field_table = Table(
    "field",
    metadata,
    Column("id", String, primary_key=True),
    Column(
        "prototype_id",
        String,
        ForeignKey("prototype.id", ondelete="cascade", name="prototype_id_fkey"),
        nullable=False,
    ),
    Column("name", String, nullable=False),
    Column("field_type_code", String, nullable=False),
    Column("field_type_description", JSONB, nullable=False),
    Column("mapping_type", String, nullable=False),
    Column("mapping_keys", JSONB, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
    Column("required", String, nullable=False),
    Column("read_only", Boolean, nullable=False),
    Column("confidential", Boolean, nullable=False),
    UniqueConstraint("name", "prototype_id", name="field_name_prototype_id_uc"),
)
