from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Path, Query, Response, UploadFile, status

from deps_prototype.application import (
    ReferenceLayoutService,
    ReferenceLayoutServiceWithSagas,
)
from deps_prototype.containers import Containers

from ...auth import get_current_user_tenant
from ...serializers.v1 import (
    CreateReferenceLayoutResponse,
    FindReferenceLayoutsResponse,
    SerializedReferenceLayout,
)
from ..marker import MarkerRoute, Visibility

__all__ = ["layout_router"]

layout_router = APIRouter(prefix="/prototypes", route_class=MarkerRoute, tags=["Reference layout"])


@layout_router.get(
    "/{prototypeId}/layouts",
    status_code=status.HTTP_200_OK,
    response_model=FindReferenceLayoutsResponse,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def find_layouts(
    prototype_id: str = Path(..., alias="prototypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    reference_layout_service: ReferenceLayoutService = Depends(Provide[Containers.reference_layout]),
):
    reference_layouts = reference_layout_service.find_layouts(
        prototype_id=prototype_id,
        tenant_id=tenant_id,
    )
    return FindReferenceLayoutsResponse.from_model(reference_layouts=reference_layouts)


@layout_router.get(
    "/{prototypeId}/layouts/{layoutId}",
    status_code=status.HTTP_200_OK,
    response_model=SerializedReferenceLayout,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def find_layout(
    prototype_id: str = Path(..., alias="prototypeId"),
    layout_id: str = Path(..., alias="layoutId"),
    tenant_id: str = Depends(get_current_user_tenant),
    reference_layout_service: ReferenceLayoutService = Depends(Provide[Containers.reference_layout]),
):
    reference_layout = reference_layout_service.get_layout(
        reference_layout_id=layout_id,
        prototype_id=prototype_id,
        tenant_id=tenant_id,
    )
    return SerializedReferenceLayout.from_model(reference_layout)


@layout_router.post(
    "/{prototypeId}/layouts",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateReferenceLayoutResponse,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def create_reference_layout(
    file: UploadFile = File(...),
    prototype_id: str = Path(..., alias="prototypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    reference_layout_service: ReferenceLayoutServiceWithSagas = Depends(
        Provide[Containers.application.reference_layout_with_sagas],
    ),
) -> CreateReferenceLayoutResponse:
    reference_layout_id = reference_layout_service.create_layout(
        prototype_id=prototype_id,
        tenant_id=tenant_id,
        file_name=file.filename,
        file=file.file.read(),
    )
    return CreateReferenceLayoutResponse(id=reference_layout_id)


@layout_router.post(
    "/{prototypeId}/layouts/{layoutId}/restart",
    status_code=status.HTTP_200_OK,
    response_class=Response,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def restart_reference_layout(
    prototype_id: str = Path(..., alias="prototypeId"),
    layout_id: str = Path(..., alias="layoutId"),
    tenant_id: str = Depends(get_current_user_tenant),
    reference_layout_service: ReferenceLayoutServiceWithSagas = Depends(
        Provide[Containers.application.reference_layout_with_sagas],
    ),
) -> None:
    reference_layout_service.restart_layout_processing(
        layout_id=layout_id,
        prototype_id=prototype_id,
        tenant_id=tenant_id,
    )


@layout_router.delete(
    "/{prototypeId}/layouts/{layoutId}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
@inject
def delete_reference_layout(
    prototype_id: str = Path(..., alias="prototypeId"),
    layout_id: str = Path(..., alias="layoutId"),
    tenant_id: str = Depends(get_current_user_tenant),
    reference_layout_service: ReferenceLayoutService = Depends(Provide[Containers.reference_layout]),
) -> None:
    reference_layout_service.delete_layout(prototype_id=prototype_id, layout_id=layout_id, tenant_id=tenant_id)


@layout_router.delete(
    "/{prototypeId}/layouts",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
@inject
def delete_reference_layouts(
    layout_ids: list[str] = Query(..., alias="layoutIds"),
    prototype_id: str = Path(..., alias="prototypeId"),
    tenant_id: str = Depends(get_current_user_tenant),
    reference_layout_service: ReferenceLayoutService = Depends(Provide[Containers.reference_layout]),
) -> None:
    reference_layout_service.delete_layouts(prototype_id=prototype_id, layout_ids=layout_ids, tenant_id=tenant_id)
