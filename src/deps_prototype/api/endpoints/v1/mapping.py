from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, status

from deps_prototype.application import MappingService, TabularMappingService
from deps_prototype.containers import Containers
from deps_prototype.domain.model import UniqueList

from ...auth import get_current_user_tenant
from ...serializers.v1 import (
    CreateMappingRequest,
    CreateTabularMappingRequest,
    ModifyMappingRequest,
    SerializedMapping,
    SerializedTabularMapping,
    UpdateTabularMappingRequest,
)
from ..marker import MarkerRoute, Visibility

__all__ = ["mapping_router"]


mapping_router = APIRouter(prefix="/prototypes", route_class=MarkerRoute, tags=["Mapping"])


@mapping_router.post(
    "/{prototypeId}/mappings",
    status_code=status.HTTP_201_CREATED,
    response_model=SerializedMapping,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def create_mapping(
    data: CreateMappingRequest,
    prototype_id: str = Path(..., alias="prototypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    mapping_service: MappingService = Depends(Provide[Containers.application.mapping]),
) -> SerializedMapping:
    return SerializedMapping.from_model(
        mapping_service.create_mapping(
            code=data.code,
            prototype_id=prototype_id,
            tenant_id=tenant_id,
            data_type=data.data_type,
            keys=UniqueList(data.keys),
            mapping_type=data.mapping_type,
        ),
    )


@mapping_router.put(
    "/{prototypeId}/mappings/{code}",
    status_code=status.HTTP_200_OK,
    response_model=SerializedMapping,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def modify_mapping(
    data: ModifyMappingRequest,
    prototype_id: str = Path(..., alias="prototypeId"),
    code: str = Path(..., alias="code"),
    tenant_id: str = Depends(get_current_user_tenant),
    mapping_service: MappingService = Depends(Provide[Containers.application.mapping]),
) -> SerializedMapping:
    return SerializedMapping.from_model(
        mapping_service.modify_mapping(
            prototype_id=prototype_id,
            mapping_code=code,
            tenant_id=tenant_id,
            keys=UniqueList(data.keys),
        ),
    )


@mapping_router.post(
    "/{prototypeId}/tabular-mappings",
    status_code=status.HTTP_201_CREATED,
    response_model=SerializedTabularMapping,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def create_tabular_mapping(
    request: CreateTabularMappingRequest,
    prototype_id: str = Path(..., alias="prototypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    tabular_mapping_service: TabularMappingService = Depends(Provide[Containers.application.tabular_mapping]),
):
    tabular_mapping = tabular_mapping_service.create_tabular_mapping(
        code=request.code,
        prototype_id=prototype_id,
        tenant_id=tenant_id,
        header_type=request.header_type,
        headers=request.raw_headers,
        occurrence_index=request.occurrence_index,
    )

    return SerializedTabularMapping.from_model(tabular_mapping)


@mapping_router.patch(
    "/{prototypeId}/tabular-mappings/{code}",
    status_code=status.HTTP_200_OK,
    response_model=SerializedTabularMapping,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def update_tabular_mapping(
    update_mapping_request: UpdateTabularMappingRequest,
    prototype_id: str = Path(..., alias="prototypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    code: str = Path(...),
    tabular_mapping_service: TabularMappingService = Depends(Provide[Containers.application.tabular_mapping]),
):
    return SerializedTabularMapping.from_model(
        tabular_mapping_service.update_tabular_mapping(
            prototype_id=prototype_id,
            tenant_id=tenant_id,
            code=code,
            header_type=update_mapping_request.header_type,
            headers=update_mapping_request.raw_headers,
            occurrence_index=update_mapping_request.occurrence_index,
        ),
    )
