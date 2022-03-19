"""Common definitions for retail chains"""

import enum
import uuid

import pydantic


class RetailChain(enum.Enum):
    """Identifies grocery store chain

    Each chain is assumed to have distinct API to fetch products/prices.
    """

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
    external_id: pydantic.constr(max_length=31)
    name: pydantic.constr(max_length=255)

    @pydantic.root_validator(pre=True)
    def create_store_id(cls, values):
        if "id" not in values:
            values["id"] = _get_store_id(values["chain"], values["external_id"])
        return values


class Price(pydantic.BaseModel):
    """Price of a single item in a store"""
    store_id: uuid.UUID
    ean: pydantic.constr(regex=r"\d{13}")
    name: pydantic.constr(max_length=255)
    price: pydantic.condecimal(max_digits=7, decimal_places=2)
