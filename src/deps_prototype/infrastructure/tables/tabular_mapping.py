from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_prototype.extras.datasource import metadata

__all__ = ["tabular_mapping_table"]

tabular_mapping_table = Table(
    "tabular_mapping",
    metadata,
    Column("code", String, primary_key=True),
    Column(
        "prototype_id",
        String,
        ForeignKey("prototype.id", ondelete="cascade", name="tabular_mapping_prototype_id_fkey"),
        nullable=False,
    ),
    Column("header_type", String, nullable=False),
    Column("headers", JSONB, nullable=False),
    Column("occurrence_index", Integer, nullable=False),
    Column("created_at", DateTime, nullable=False),
)
