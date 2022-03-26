"""API models"""

import decimal
import uuid
import typing

import pydantic

import hrefs
from hrefs.starlette import ReferrableModel

from ..retail import RetailChain, Name, Ean, Price


class Store(ReferrableModel):
    """A grocery store"""

    self: hrefs.Href["Store"]
    id: uuid.UUID
    chain: RetailChain
    name: Name

    # pylint: disable=all
    @pydantic.root_validator(pre=True)
    def _populate_self(cls, values):
        values["self"] = values["id"]
        return values

    class Config:
        details_view = "get_store"


Store.update_forward_refs()


class Product(ReferrableModel):
    """A single product within a given store

    There is no store independent product model.  Although the same product (by
    EAN code) may (and often is) sold in different stores, it may have different
    name or price.
    """

    self: hrefs.Href["Product"]
    store: typing.Annotated[hrefs.Href[Store], hrefs.PrimaryKey]
    ean: typing.Annotated[Ean, hrefs.PrimaryKey]
    name: Name
    price: Price

    # pylint: disable=all
    @pydantic.root_validator(pre=True)
    def _populate_self(cls, values):
        values["self"] = values["store"], values["ean"]
        return values

    class Config:
        details_view = "get_product"


Product.update_forward_refs()


class CartProduct(pydantic.BaseModel):
    """Product and quantity"""

    product: hrefs.Href[Product]
    quantity: pydantic.PositiveInt


class _StoreVisitBase(pydantic.BaseModel):
    store: hrefs.Href[Store]
    cart: list[CartProduct]


class StoreVisit(_StoreVisitBase, ReferrableModel):
    """State of a single store visit"""

    self: hrefs.Href["StoreVisit"]
    id: uuid.UUID

    # pylint: disable=all
    @pydantic.root_validator(pre=True)
    def _populate_self(cls, values):
        values["self"] = values["id"]
        return values

    class Config:
        details_view = "get_store_visit"


StoreVisit.update_forward_refs()


class StoreVisitCreate(_StoreVisitBase):
    """Payload for creating a store visit"""

    cart: list[CartProduct] = []
