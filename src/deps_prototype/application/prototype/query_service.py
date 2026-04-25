import logging

from deps_prototype.domain.exceptions import PrototypeNotFound
from deps_prototype.domain.model import IQueryPrototypeRepository, PrototypeWithMappings

__all__ = ["QueryPrototypeService"]


class QueryPrototypeService:
    def __init__(
        self,
        query_prototype_repository: IQueryPrototypeRepository,
    ) -> None:
        self._query_prototype_repository = query_prototype_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    def find_prototype(self, id_: str, tenant_id: str) -> PrototypeWithMappings:
        if prototype := self._query_prototype_repository.find_prototype_with_mappings(id_=id_, tenant_id=tenant_id):
            return prototype

        raise PrototypeNotFound(id_)
