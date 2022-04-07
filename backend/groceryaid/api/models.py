"""API models"""

import collections
import decimal
import uuid
import typing

import pydantic

import hrefs
from hrefs.starlette import ReferrableModel

from ..retail import RetailChain, Name, Ean, Price


class Store(ReferrableModel):
    """A grocery store"""

    self: hrefs.Href["Store"] = pydantic.Field(
        title="Self hyperlink", description="The URL of the store"
    )
    id: uuid.UUID
    chain: RetailChain = pydantic.Field(
        description="The retail chain this store belongs to"
    )
    name: Name = pydantic.Field(description="The name of the store")

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

    self: hrefs.Href["Product"] = pydantic.Field(
        title="Self hyperlink", description="The URL of the product"
    )
    store: typing.Annotated[hrefs.Href[Store], hrefs.PrimaryKey] = pydantic.Field(
        title="Store hyperlink",
        description="The store this product is sold in",
    )
    ean: typing.Annotated[Ean, hrefs.PrimaryKey] = pydantic.Field(
        description="The EAN code of the product",
    )
    name: Name = pydantic.Field(description="The name of the product")
    price: Price = pydantic.Field(description="The price per unit")

    # pylint: disable=all
    @pydantic.root_validator(pre=True)
    def _populate_self(cls, values):
        values["self"] = values["store"], values["ean"]
        return values

    class Config:
        details_view = "get_product"


Product.update_forward_refs()


class _CartProductBase(pydantic.BaseModel):
    quantity: pydantic.PositiveInt


class CartProduct(_CartProductBase):
    """Product and quantity"""

    product: Product
    total_price: Price


class _StoreVisitBase(pydantic.BaseModel):
    store: hrefs.Href[Store] = pydantic.Field(
        title="Store hyperlink",
        description="The store this store visit takes place in",
    )


class StoreVisit(_StoreVisitBase, ReferrableModel):
    """State of a single store visit"""

    self: hrefs.Href["StoreVisit"] = pydantic.Field(
        title="Self hyperlink", description="The URL of the store visit"
    )
    id: uuid.UUID
    cart: list[CartProduct] = pydantic.Field(description="The items in the cart")

    # pylint: disable=all
    @pydantic.root_validator(pre=True)
    def _populate_self(cls, values):
        values["self"] = values["id"]
        return values

    @pydantic.validator("cart")
    def _ensure_cart_is_ordered(cls, cart: list[CartProduct]):
        cart.sort(key=lambda cartproduct: cartproduct.product.ean)
        return cart

    class Config:
        details_view = "get_store_visit"


StoreVisit.update_forward_refs()


class CartProductCreate(_CartProductBase):
    """Payload for creating a product in cart"""

    product: Product | hrefs.Href[Product] | Ean = pydantic.Field(
        description="""
                    Product is identified either by hyperlink or EAN number.  In
                    the latter case the store is inferred from the context.
                    """
    )

    def get_ean(self) -> Ean:
        """Get EAN code of the product"""
        if isinstance(self.product, Product):
            return self.product.ean
        elif isinstance(self.product, Ean):
            return self.product
        return self.product.key.ean


class _CartCreateMixin(pydantic.BaseModel):
    cart: list[CartProductCreate] = pydantic.Field(
        [],
        description="""The items in the cart.  Each product in the cart must be
                    unique.  To represent multiple products, use the
                    ``quantity`` attribute of the cart products.
                    """,
    )

    def get_eans(self) -> typing.Iterable[Ean]:
        """Get all EANs of this cart"""
        for cartproduct in self.cart:
            yield cartproduct.get_ean()

    @pydantic.validator("cart")
    def validate_cart_has_unique_products(cls, cart: list[CartProductCreate]):
        eans = collections.Counter(cartproduct.get_ean() for cartproduct in cart)
        duplicate_eans = list(ean for (ean, count) in eans.items() if count > 1)
        if duplicate_eans:
            raise ValueError(f"Duplicate EAN codes: {', '.join(duplicate_eans)}")
        return cart


class StoreVisitCreate(_CartCreateMixin, _StoreVisitBase):
    """Payload for creating a store visit"""


class StoreVisitUpdate(_CartCreateMixin):
    """Payload for updating a store visit"""
