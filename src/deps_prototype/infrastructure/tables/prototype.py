from sqlalchemy import JSON, Column, DateTime, String, Table, UniqueConstraint

from deps_prototype.extras.datasource import metadata

__all__ = ["prototype_table"]


prototype_table = Table(
    "prototype",
    metadata,
    Column("id", String(100), primary_key=True),
    Column("tenant_id", String(100), nullable=False),
    Column("name", String(150), nullable=False),
    Column("engine", String(150), nullable=False),
    Column("language", String(150), nullable=False),
    Column("description", String(150)),
    Column("created_at", DateTime, nullable=False),
    Column("field_names", JSON, nullable=False),
    UniqueConstraint("name", "tenant_id", name="prototype_name_tenant_id_uc"),
)
