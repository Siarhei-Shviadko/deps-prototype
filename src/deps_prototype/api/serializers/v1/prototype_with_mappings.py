from pydantic import Field

from deps_prototype.domain.model import PrototypeWithMappings

from .mapping import SerializedMapping
from .prototype import SerializedPrototype
from .tabular_mapping import SerializedTabularMapping

__all__ = ["SerializedPrototypeWithMappings"]


class SerializedPrototypeWithMappings(SerializedPrototype):
    mappings: list[SerializedMapping]
    tabular_mappings: list[SerializedTabularMapping] = Field(..., alias="tabularMappings")

    @classmethod
    def from_model(cls, prototype_with_mappings: PrototypeWithMappings) -> "SerializedPrototypeWithMappings":
        prototype = prototype_with_mappings["prototype"]

        return cls(
            id=prototype.id(),
            name=prototype.name,
            engine=prototype.engine,
            language=prototype.language,
            created_at=prototype.created_at,
            description=prototype.description,
            mappings=[SerializedMapping.from_model(mapping) for mapping in prototype_with_mappings["mappings"]],
            tabular_mappings=[
                SerializedTabularMapping.from_model(tabular_mapping)
                for tabular_mapping in prototype_with_mappings["tabular_mappings"]
            ],
        )
