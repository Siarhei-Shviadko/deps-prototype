from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_prototype.extras.datasource import metadata

__all__ = ["mapping_table"]

mapping_table = Table(
    "mapping",
    metadata,
    Column("code", String, primary_key=True),
    Column(
        "prototype_id",
        String,
        ForeignKey("prototype.id", ondelete="cascade", name="mapping_prototype_id_fkey"),
        nullable=False,
    ),
    Column("data_type_code", String, nullable=False),
    Column("mapping_type", String, nullable=False),
    Column("mapping_keys", JSONB, nullable=False),
    Column("created_at", DateTime, nullable=False),
)
