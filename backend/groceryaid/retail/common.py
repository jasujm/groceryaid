"""Common definitions for retail chains"""

import decimal
import enum
import uuid
import re
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


if typing.TYPE_CHECKING:
    ExternalId = str
    Name = str
    Price = decimal.Decimal
    Quantity = int

else:
    ExternalId = pydantic.constr(max_length=36)
    Name = pydantic.constr(max_length=255)
    Price = pydantic.condecimal(max_digits=7, decimal_places=2)
    Quantity = pydantic.conint(ge=1, le=999)


class Ean(str):
    """EAN code"""

    prefix_pattern = re.compile(r"\A[0-9]{12}\Z")
    variable_price_prefix_pattern = re.compile(r"\A2[0-9]{11}\Z")
    pattern = re.compile(r"\A[0-9]{13}\Z")

    def is_variable_price(self):
        """Return ``True`` if this is a variable price EAN"""
        return self.startswith("2")

    def get_ean_for_query(self) -> "Ean":
        """Return EAN in normalized database format

        For variable price EANs, it is the EAN identifying the same product, but
        with price 0.

        For fixed price EAN, it is the EAN itself.
        """
        if self.is_variable_price():
            return self.from_prefix(self[:8] + "0000")
        return self

    def get_ean_with_price(self, price: Price) -> "Ean":
        """Return EAN with given price

        This only works for variable price EAN.

        Raises:
            ValueError if this is not variable price EAN
        """
        if not self.is_variable_price():
            raise ValueError(f"{self!r} is not variable price EAN code")
        if not 0 < price < 100:
            raise ValueError("f{price} is out of range")
        encoded_price = str(int(price.scaleb(2))).rjust(4, "0")
        return self.from_prefix(self[:8] + encoded_price)

    def get_price(self) -> typing.Optional[Price]:
        """Return price encoded in the EAN

        Returns:
            The encoded price for variable price EAN, or ``None`` for fixed
            price EAN
        """
        if self.is_variable_price():
            return Price(self[8:12]).scaleb(-2)
        return None

    @staticmethod
    def calculate_check_digit(prefix: str) -> str:
        """Calculates check digit for 12 letter EAN prefix"""
        checksum = sum(int(c) for c in prefix[0::2]) + 3 * sum(
            int(c) for c in prefix[1::2]
        )
        checksum %= 10
        if checksum == 0:
            return "0"
        return str(10 - checksum)

    @classmethod
    def from_prefix(cls, prefix: str) -> "Ean":
        """Return EAN from 12 letter EAN prefix"""
        return cls(prefix + cls.calculate_check_digit(prefix))

    @classmethod
    def validate(cls, value: str):
        if (
            not cls.pattern.fullmatch(value)
            or cls.calculate_check_digit(value[:12]) != value[12]
        ):
            raise ValueError(f"{value!r} is not valid EAN number")
        return cls(value)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema["pattern"] = cls.pattern.pattern


class Store(pydantic.BaseModel):
    """A grocery store"""

    id: uuid.UUID
    chain: RetailChain
    external_id: ExternalId
    name: Name

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

    @pydantic.validator("price", pre=True)
    def _round_price(cls, price):
        if isinstance(price, float):
            return round(price, 2)
        return price


class CartProduct(pydantic.BaseModel):
    """Product and quantity"""

    ean: Ean
    name: typing.Optional[Name]
    price: typing.Optional[Price]
    quantity: typing.Optional[Quantity]

    def is_variable_price(self):
        """Return ``True`` if the cart product is variable price

        A cart product is variable price, if its quantity is zero.  Variable
        price products are indivisible.
        """
        return self.quantity is None

    def get_total_price(self) -> typing.Optional[Price]:
        """Return the total price of the cart product, if known"""
        if self.price is not None:
            return (self.quantity or 1) * self.price
        return None


class StoreVisit(pydantic.BaseModel):
    """State of a single store visit"""

    id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    store_id: uuid.UUID
    cart: list[CartProduct]
