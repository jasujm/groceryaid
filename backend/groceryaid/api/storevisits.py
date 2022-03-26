"""Stores API"""

import uuid

import fastapi

from .models import StoreVisit, StoreVisitCreate

from ..retail import storevisits

router = fastapi.APIRouter()


@router.get("/{id}", response_model=StoreVisit)
async def get_store_visit(id: uuid.UUID):
    """
    Retrieve information about store visit identified by ``id``
    """
    if storevisit := await storevisits.read_store_visit(id):
        store_id = storevisit.store_id
        return {
            "id": id,
            "store": store_id,
            "cart": [
                {
                    "product": (store_id, product.ean),
                    **product.dict(),
                }
                for product in storevisit.cart
            ],
        }
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        detail=f"Store visit {id=!r} not found",
    )


@router.post("", status_code=fastapi.status.HTTP_201_CREATED)
async def post_store_visit(
    storevisit: StoreVisitCreate, response: fastapi.Response, request: fastapi.Request
):
    """
    Create a new store visit
    """
    new_storevisit = storevisits.StoreVisit(
        store_id=storevisit.store.key,
        cart=[
            {
                "ean": cartproduct.product.key.ean,
                **cartproduct.dict(),
            }
            for cartproduct in storevisit.cart
        ],
    )
    await storevisits.create_store_visit(new_storevisit)
    response.headers["Location"] = request.url_for(
        "get_store_visit", id=new_storevisit.id
    )
