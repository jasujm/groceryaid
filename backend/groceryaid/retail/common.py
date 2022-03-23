"""Common definitions for retail chains"""

import decimal
import enum
import uuid
import typing

import pydantic


class RetailChain(enum.Enum):
    """Identifies grocery store chain

    Each chain is assumed to have distinct API to fetch products/prices.
    """

    FAKER = "faker"
    SOK = "sok"


# TODO: store in environment
_store_root_namespace = uuid.uuid4()

_store_namespaces = {
    chain: uuid.uuid5(_store_root_namespace, str(chain)) for chain in RetailChain
}


def _get_store_id(chain: RetailChain, external_id) -> uuid.UUID:
    return uuid.uuid5(_store_namespaces[chain], str(external_id))


class Store(pydantic.BaseModel):
    """A grocery store in chain supported by the app"""

    id: uuid.UUID
    chain: RetailChain
    external_id: typing.Annotated[str, pydantic.Field(max_length=36)]
    name: typing.Annotated[str, pydantic.Field(max_length=255)]

    # pylint: disable=all
    @pydantic.root_validator(pre=True)
    def create_store_id(cls, values):
        if "id" not in values:
            values["id"] = _get_store_id(values["chain"], values["external_id"])
        return values


class Price(pydantic.BaseModel):
    """Price of a single item in a store"""

    store_id: uuid.UUID
    ean: typing.Annotated[str, pydantic.Field(regex=r"\d{13}")]
    name: typing.Annotated[str, pydantic.Field(max_length=255)]
    price: typing.Annotated[
        decimal.Decimal, pydantic.Field(max_digits=7, decimal_places=2)
    ]
