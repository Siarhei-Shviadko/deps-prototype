from dataclasses import dataclass
from typing import Any

__all__ = ["DocumentTypeData"]


@dataclass
class DocumentTypeData:
    id: str

    @classmethod
    def from_dict(cls, document_type_data: dict[str, Any]) -> "DocumentTypeData":
        return cls(
            id=document_type_data["documentTypeId"],
        )
