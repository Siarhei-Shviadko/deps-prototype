from sqlalchemy import Column, ForeignKey, String, Table

from deps_prototype.extras.datasource import metadata

__all__ = ["reference_layout_table"]

reference_layout_table = Table(
    "reference_layout",
    metadata,
    Column("id", String, primary_key=True),
    Column(
        "prototype_id",
        String,
        ForeignKey("prototype.id", ondelete="cascade", name="prototype_id_fkey"),
        nullable=False,
    ),
    Column("state", String, nullable=False),
    Column("blob_name", String, nullable=False),
    Column("title", String, nullable=True),
)
