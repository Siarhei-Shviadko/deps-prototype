from datetime import datetime
from http import HTTPStatus

from dateutil import parser
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Query, Response, status
from fastapi.exceptions import HTTPException

from deps_prototype.application import PrototypeService, QueryPrototypeService
from deps_prototype.containers import Containers
from deps_prototype.domain.model import (
    Pagination,
    PrototypeSortingField,
    SortingDirection,
)

from ...auth import get_current_user_tenant
from ...serializers.v1 import (
    CreatePrototypeRequest,
    CreatePrototypeResponse,
    FindPrototypesResponse,
    SerializedPrototype,
    SerializedPrototypeWithMappings,
    UpdatePrototypeRequest,
)
from ..marker import MarkerRoute, Visibility

__all__ = ["prototype_router"]

prototype_router = APIRouter(prefix="/prototypes", route_class=MarkerRoute, tags=["Prototype"])


def parse_datetime(dt: str | None) -> datetime | None:
    try:
        return parser.parse(dt) if dt is not None else None
    except parser.ParserError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))


@prototype_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CreatePrototypeResponse,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def create_prototype(
    create_request: CreatePrototypeRequest,
    current_tenant_id: str = Depends(get_current_user_tenant),
    prototype_service: PrototypeService = Depends(Provide[Containers.application.prototype]),
):
    prototype_id = prototype_service.create_prototype(
        tenant_id=current_tenant_id,
        name=create_request.name,
        description=create_request.description,
        engine=create_request.engine,
        language=create_request.language,
    )
    return CreatePrototypeResponse(id=prototype_id)


@prototype_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=FindPrototypesResponse,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def find_prototypes(
    ids: list[str] | None = Query(None, alias="id"),
    name: str | None = Query(None),
    engines: list[str] | None = Query(None, alias="engine"),
    languages: list[str] | None = Query(None, alias="language"),
    page: int | None = Query(Pagination.page, ge=1),
    per_page: int | None = Query(Pagination.per_page, ge=1, alias="perPage"),
    start_date: str | None = Query(None, alias="startDate"),
    end_date: str | None = Query(None, alias="endDate"),
    sorting_field: PrototypeSortingField = Query(PrototypeSortingField.CREATED_AT, alias="sortField"),
    sorting_direction: SortingDirection = Query(SortingDirection.DESC, alias="sortDirect"),
    current_tenant_id: str = Depends(get_current_user_tenant),
    prototype_service: PrototypeService = Depends(Provide[Containers.application.prototype]),
):
    prototypes, meta = prototype_service.find_prototypes(
        ids=ids,
        name=name,
        engines=engines,
        languages=languages,
        page=page,
        per_page=per_page,
        start_date=parse_datetime(start_date),
        end_date=parse_datetime(end_date),
        sorting_field=sorting_field,
        sorting_direction=sorting_direction,
        tenant_id=current_tenant_id,
    )
    return FindPrototypesResponse.from_model(prototypes=prototypes, meta=meta)


@prototype_router.patch(
    "/{prototypeId}",
    status_code=status.HTTP_200_OK,
    response_model=SerializedPrototype,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def update_prototype(
    update_prototype_request: UpdatePrototypeRequest,
    prototype_id: str = Path(..., alias="prototypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    prototype_service: PrototypeService = Depends(Provide[Containers.application.prototype]),
) -> SerializedPrototype:
    return SerializedPrototype.from_model(
        prototype_service.update_prototype(
            id_=prototype_id,
            tenant_id=tenant_id,
            engine=update_prototype_request.engine,
            language=update_prototype_request.language,
            description=update_prototype_request.description,
        ),
    )


@prototype_router.get(
    "/{prototypeId}",
    status_code=status.HTTP_200_OK,
    response_model=SerializedPrototypeWithMappings,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def find_prototype(
    prototype_id: str = Path(..., alias="prototypeId"),
    current_tenant_id: str = Depends(get_current_user_tenant),
    query_prototype_service: QueryPrototypeService = Depends(Provide[Containers.application.query_prototype]),
):
    prototype_with_mappings = query_prototype_service.find_prototype(id_=prototype_id, tenant_id=current_tenant_id)

    return SerializedPrototypeWithMappings.from_model(prototype_with_mappings)


@prototype_router.delete(
    "/{prototypeId}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def delete_prototype(
    prototype_id: str = Path(..., alias="prototypeId"),
    current_tenant_id: str = Depends(get_current_user_tenant),
    prototype_service: PrototypeService = Depends(Provide[Containers.application.prototype]),
):
    prototype_service.delete_prototype(id_=prototype_id, tenant_id=current_tenant_id)


@prototype_router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def delete_prototypes(
    ids: list[str] = Query(...),
    current_tenant_id: str = Depends(get_current_user_tenant),
    prototype_service: PrototypeService = Depends(Provide[Containers.application.prototype]),
):
    prototype_service.delete_prototypes(ids=ids, tenant_id=current_tenant_id)
