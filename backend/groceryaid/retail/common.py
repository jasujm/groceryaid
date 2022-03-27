"""Common definitions for retail chains"""

import decimal
import enum
import uuid
import typing

import pydantic

from ..settings import settings


class RetailChain(enum.Enum):
    """Identifies grocery store chain"""

    FAKER = "faker"
    SOK = "sok"


_store_namespaces = {
    chain: uuid.uuid5(settings.store_root_namespace, chain.value)
    for chain in RetailChain
}


def _get_store_id(chain: RetailChain, external_id) -> uuid.UUID:
    return uuid.uuid5(_store_namespaces[chain], str(external_id))


def _get_product_id(store_id, ean: str) -> uuid.UUID:
    if not isinstance(store_id, uuid.UUID):
        store_id = uuid.UUID(store_id)
    return uuid.uuid5(store_id, ean)


ExternalId = typing.Annotated[str, pydantic.Field(max_length=36)]
Name = typing.Annotated[str, pydantic.Field(max_length=255)]
Ean = typing.Annotated[str, pydantic.Field(regex=r"\d{13}")]
Price = typing.Annotated[
    decimal.Decimal, pydantic.Field(max_digits=7, decimal_places=2)
]


class Store(pydantic.BaseModel):
    """A grocery store"""

    id: uuid.UUID
    chain: RetailChain
    external_id: ExternalId
    name: Name

    # pylint: disable=all
    @pydantic.root_validator(pre=True)
    def _create_store_id(cls, values):
        if "id" not in values:
            values["id"] = _get_store_id(values["chain"], values["external_id"])
        return values


class Product(pydantic.BaseModel):
    """A single product within a given store

    There is no store independent product model.  Although the same product (by
    EAN code) may (and often is) sold in different stores, it may have different
    name or price.
    """

    id: uuid.UUID
    store_id: uuid.UUID
    ean: Ean
    name: Name
    price: Price

    # pylint: disable=all
    @pydantic.root_validator(pre=True)
    def _create_product_id(cls, values):
        if "id" not in values:
            values["id"] = _get_product_id(values["store_id"], values["ean"])
        return values


class CartProduct(pydantic.BaseModel):
    """Product and quantity"""

    product_id: uuid.UUID
    store_id: typing.Optional[uuid.UUID]
    ean: typing.Optional[Ean]
    quantity: pydantic.PositiveInt

    # pylint: disable=all
    @pydantic.root_validator(pre=True)
    def _create_product_id(cls, values):
        if "product_id" not in values:
            values["product_id"] = _get_product_id(values["store_id"], values["ean"])
        return values


class StoreVisit(pydantic.BaseModel):
    """State of a single store visit"""

    id: typing.Annotated[uuid.UUID, pydantic.Field(default_factory=uuid.uuid4)]
    store_id: uuid.UUID
    cart: list[CartProduct]
