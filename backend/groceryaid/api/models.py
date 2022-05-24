"""API models"""

import collections
import decimal
import uuid
import typing

import pydantic

import hrefs
from hrefs.starlette import ReferrableModel

from ..retail import RetailChain, Name, Ean, Price, Quantity


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
    quantity: typing.Optional[Quantity] = pydantic.Field(
        description="""Number of items

                    For a variable price product, this is always ``null``
                    """
    )

    def is_variable_price(self):
        return self.quantity is None


class CartProduct(_CartProductBase):
    """Product and quantity"""

    product: Product
    total_price: decimal.Decimal = pydantic.Field(
        ge=0, description="Price times quantity"
    )


class CartProductCreate(_CartProductBase):
    """Payload for creating a product in cart"""

    product: Product | hrefs.Href[Product] | Ean = pydantic.Field(
        description="""
                    Product is identified either by hyperlink or EAN number.  In
                    the latter case the store is inferred from the context.
                    """
    )

    @staticmethod
    def _get_ean_from_product(product):
        if isinstance(product, Product):
            return product.ean
        elif isinstance(product, Ean):
            return product
        return product.key.ean

    def get_ean(self) -> Ean:
        """Get EAN code of the product"""
        return self._get_ean_from_product(self.product)

    def get_ean_for_query(self) -> Ean:
        """Get EAN code of the product for database query"""
        return self.get_ean().get_ean_for_query()

    def get_price(self) -> typing.Optional[Price]:
        """Get price of the product"""
        if isinstance(self.product, Product):
            return self.product.price
        return self.get_ean().get_price()

    @pydantic.root_validator()
    def _ensure_variable_price_product_has_no_quantity(cls, values):
        is_variable_price = cls._get_ean_from_product(
            values["product"]
        ).is_variable_price()
        has_quantity = values["quantity"] is not None
        if is_variable_price and has_quantity:
            raise ValueError("Variable price product must not have quantity")
        elif not is_variable_price and not has_quantity:
            raise ValueError("Fixed price product must have quantity")
        return values


class Cart(pydantic.BaseModel):
    """Cart containing products"""

    items: list[CartProduct] = pydantic.Field(description="The items in the cart")
    total_price: decimal.Decimal = pydantic.Field(
        ge=0, description="Total price of all items"
    )

    @pydantic.validator("items")
    def _ensure_items_are_ordered(cls, items: list[CartProduct]):
        items.sort(key=lambda item: item.product.ean)
        return items


class CartCreate(pydantic.BaseModel):
    items: list[CartProductCreate] = pydantic.Field(
        [],
        description="""The items in the cart.  Each product in the cart must be
                    unique.  To represent multiple products, use the
                    ``quantity`` attribute of the cart products.
                    """,
    )

    def get_eans(self) -> typing.Iterable[Ean]:
        """Get all EANs of this cart"""
        for item in self.items:
            yield item.get_ean()


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
    cart: Cart

    # pylint: disable=all
    @pydantic.root_validator(pre=True)
    def _populate_self(cls, values):
        values["self"] = values["id"]
        return values

    class Config:
        details_view = "get_store_visit"


StoreVisit.update_forward_refs()


class _CartCreateMixin(pydantic.BaseModel):
    cart: CartCreate = pydantic.Field(default_factory=CartCreate)


class StoreVisitCreate(_CartCreateMixin, _StoreVisitBase):
    """Payload for creating a store visit"""


class StoreVisitUpdate(_CartCreateMixin):
    """Payload for updating a store visit"""


class GroupedCart(pydantic.BaseModel):
    """Cart with items grouped into fixed bins"""

    store_visit: hrefs.Href[StoreVisit]
    binned_cart: list[Cart]
