from deps_prototype.application import IDocumentTypeProxy

__all__ = ["FakeDocumentTypeProxy"]


class FakeDocumentTypeProxy(IDocumentTypeProxy):
    def delete_document_type(self, document_type_id: str) -> None:
        pass
