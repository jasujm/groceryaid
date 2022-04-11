"""Stores API"""

import typing
import uuid

import fastapi
import jsonpatch
import jsonpointer
import pydantic
import sqlalchemy
import sqlalchemy.ext.asyncio as sqlaio

from .models import StoreVisit, StoreVisitCreate, StoreVisitUpdate

from .. import db
from ..retail import storevisits
from ..retail import StoreVisit as DbStoreVisit, CartProduct as DbCartProduct

router = fastapi.APIRouter()

_JSON_PATCH_CONTENT_TYPE = "application/json-patch+json"

_RESPONSE_404 = {
    "description": "Store visit not found",
}

_ProductProxy = typing.Mapping[str, typing.Any]


async def _get_json_patch(
    request: fastapi.Request,
    body=fastapi.Body(..., media_type=_JSON_PATCH_CONTENT_TYPE),
) -> jsonpatch.JsonPatch:
    if (
        content_type := request.headers.get("content-type")
    ) != _JSON_PATCH_CONTENT_TYPE:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Expected content type {_JSON_PATCH_CONTENT_TYPE!r}, got: {content_type!r}",
        )
    try:
        return jsonpatch.JsonPatch(body)
    except jsonpatch.InvalidJsonPatch as ex:
        # To simulate the pydantic error style FastAPI uses... there could
        # potentially be fancier way to achieve this
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "loc": "body",
                    "msg": str(ex),
                    "type": "value_error.invalidjsonpatch",
                }
            ],
        ) from ex


async def _get_product_records(
    connection: sqlaio.AsyncConnection,
    storevisit: StoreVisitCreate | StoreVisitUpdate,
    store_id: uuid.UUID,
) -> _ProductProxy:
    product_eans = set(storevisit.cart.get_eans())
    known_products = (
        await db.execute(
            sqlalchemy.select([db.products.c.ean, db.products.c.name, db.products.c.price]).where(  # type: ignore
                db.products.c.store_id == store_id,
                db.products.c.ean.in_(product_eans),
            ),
            connection=connection,
        )
    ).fetchall()
    known_product_eans = set(product.ean for product in known_products)
    if missing_eans := product_eans - known_product_eans:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown products: {', '.join(missing_eans)}",
        )
    return {product.ean: product for product in known_products}


def _prepare_store_visit_for_db(
    storevisit: StoreVisitCreate | StoreVisitUpdate, **kwargs
) -> DbStoreVisit:
    return DbStoreVisit(
        **kwargs,
        cart=[
            {
                "ean": item.get_ean(),
                **item.dict(exclude={"product", "ean"}),
            }
            for item in storevisit.cart.items
        ],
    )


def _prepare_cart_product_for_api(
    store_id: uuid.UUID, cartproduct: DbCartProduct, product: _ProductProxy
):
    return {
        "product": {
            "store": store_id,
            **cartproduct.dict(include={"ean", "name", "price"}),
            **product,
        },
        "quantity": cartproduct.quantity,
        "total_price": cartproduct.quantity * (cartproduct.price or product["price"]),
    }


def _prepare_store_visit_for_api(
    storevisit: DbStoreVisit, products: typing.Mapping[str, _ProductProxy]
) -> dict:
    store_id = storevisit.store_id
    items = [
        _prepare_cart_product_for_api(
            store_id, cartproduct, products.get(cartproduct.ean, {})
        )
        for cartproduct in storevisit.cart
    ]
    return {
        "id": storevisit.id,
        "store": store_id,
        "cart": {
            "items": items,
            "total_price": sum(item["total_price"] for item in items),
        },
    }


async def _get_store_visit(
    id: uuid.UUID, *, connection: typing.Optional[sqlaio.AsyncConnection] = None
):
    if storevisit := await storevisits.read_store_visit(id, connection=connection):
        return _prepare_store_visit_for_api(storevisit, {})
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        detail=f"Store visit {id=!r} not found",
    )


@router.get(
    "/{id}",
    response_model=StoreVisit,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: _RESPONSE_404,
    },
)
async def get_store_visit(id: uuid.UUID):
    """
    Retrieve information about store visit identified by ``id``
    """
    return await _get_store_visit(id)


@router.post(
    "",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=StoreVisit,
    response_description="The created store visit",
)
async def post_store_visit(
    storevisit: StoreVisitCreate, response: fastapi.Response, request: fastapi.Request
):
    """
    Create a new store visit
    """
    async with db.get_connection() as connection:
        store_id = storevisit.store.key
        store = await db.read(
            db.stores, store_id, columns=[db.stores.c.id], connection=connection
        )
        if store is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create store visit with unknown store: {store_id!r}",
            )
        products = await _get_product_records(connection, storevisit, store_id)
        new_storevisit = _prepare_store_visit_for_db(storevisit, store_id=store.id)
        await storevisits.create_store_visit(new_storevisit, connection=connection)
        response.headers["Location"] = request.url_for(
            "get_store_visit", id=new_storevisit.id
        )
        return _prepare_store_visit_for_api(new_storevisit, products)


@router.put(
    "/{id}",
    response_model=StoreVisit,
    response_description="The updated store visit",
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: _RESPONSE_404,
    },
)
async def put_store_visit(id: uuid.UUID, storevisit: StoreVisitUpdate):
    """
    Update a store visit
    """
    async with db.get_connection() as connection:
        storevisit_in_db = await db.read(
            db.storevisits,
            id,
            columns=[db.storevisits.c.store_id],
            connection=connection,
        )
        if not storevisit_in_db:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=f"Store visit {id=!r} not found",
            )
        store_id = storevisit_in_db.store_id
        products = await _get_product_records(connection, storevisit, store_id)
        new_storevisit = _prepare_store_visit_for_db(
            storevisit, id=id, store_id=store_id
        )
        await storevisits.update_store_visit(new_storevisit, connection=connection)
        return _prepare_store_visit_for_api(new_storevisit, products)


@router.patch(
    "/{id}",
    response_model=StoreVisit,
    response_description="The updated store visit",
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: _RESPONSE_404,
        fastapi.status.HTTP_409_CONFLICT: {
            "description": "Cannot apply the JSON patch in the body"
        },
    },
)
async def patch_store_visit(
    id: uuid.UUID, patch: jsonpatch.JsonPatch = fastapi.Depends(_get_json_patch)
):
    """
    Partially update a store visit

    The update happens as if by applying the JSON Patch in the body to the
    representation returned by the GET request to the same URL.  If the patch
    doesn't apply, or the resulting JSON document doesn't represent a valid
    store visit, the operation fails.  Fields that cannot be updated with a PUT
    request cannot be updated with a PATCH request either, and are ignored.
    """
    async with db.get_connection() as connection:
        old_storevisit_data = await _get_store_visit(id, connection=connection)
        old_storevisit = StoreVisit(**old_storevisit_data)
        store_id = old_storevisit.store.key
        try:
            new_storevisit_data = patch.apply(old_storevisit.dict())
        except (jsonpatch.JsonPatchException, jsonpointer.JsonPointerException) as ex:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_409_CONFLICT,
                detail=f"Failed to process JSON Patch: {ex}",
            )
        try:
            new_storevisit = StoreVisitUpdate(**new_storevisit_data)
        except pydantic.ValidationError as ex:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update store visit: {ex}",
            ) from ex
        products = await _get_product_records(connection, new_storevisit, store_id)
        new_storevisit_data = _prepare_store_visit_for_db(
            new_storevisit, id=id, store_id=store_id
        )
        await storevisits.update_store_visit(new_storevisit_data, connection=connection)
        return _prepare_store_visit_for_api(new_storevisit_data, products)
