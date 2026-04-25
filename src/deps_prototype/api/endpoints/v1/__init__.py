from fastapi import APIRouter

from ...constants import V1_PREFIX
from .mapping import mapping_router
from .prototype import prototype_router
from .reference_layout import layout_router

__all__ = ["v1_router"]


v1_router = APIRouter(prefix=V1_PREFIX)

v1_router.include_router(prototype_router)
v1_router.include_router(mapping_router)
v1_router.include_router(layout_router)
