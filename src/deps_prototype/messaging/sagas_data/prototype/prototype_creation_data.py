from typing import Any

from deps_message_flow.sagas.orchestration import SagaData

__all__ = ["PrototypeCreationSagaData"]


class PrototypeCreationSagaData(SagaData):
    def __init__(
        self,
        name: str,
        language: str,
        engine: str,
        tenant_id: str,
        *,
        description: str | None = None,
        prototype_id: str | None = None,
    ) -> None:
        super().__init__(entity_id=prototype_id)
        self.name = name
        self.language = language
        self.engine = engine
        self.tenant_id = tenant_id
        self.description = description

    @property
    def prototype_id(self) -> str | None:
        return self.entity_id

    @prototype_id.setter
    def prototype_id(self, value: str | None) -> None:
        self.entity_id = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "language": self.language,
            "engine": self.engine,
            "tenant_id": self.tenant_id,
            "entity_id": self.prototype_id,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "PrototypeCreationSagaData":
        return cls(
            name=raw_data["name"],
            language=raw_data["language"],
            engine=raw_data["engine"],
            tenant_id=raw_data["tenant_id"],
            prototype_id=raw_data.get("prototype_id"),
            description=raw_data.get("description"),
        )
