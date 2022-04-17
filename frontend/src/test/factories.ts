import { Factory } from "fishery";
import { faker } from "@faker-js/faker";

import {
  Store,
  Product,
  CartProduct,
  Cart,
  StoreVisit,
  GroupedCart,
} from "../api";

function storeUrl(storeId: string) {
  return `http://localhost/api/v1/stores/${storeId}`;
}

function productUrl(store: string, ean: string) {
  return `${store}/products/${ean}`;
}

export const storeFactory = Factory.define<Store>(({ params }) => {
  const id = params.id ?? faker.datatype.uuid();
  return {
    self: storeUrl(id),
    id,
    name: faker.address.city(),
  };
});

export const productFactory = Factory.define<Product>(({ params }) => {
  const store = params.store ?? storeUrl(faker.datatype.uuid());
  const ean = params.ean ?? "1234567890123";
  return {
    self: productUrl(store, ean),
    store,
    ean,
    name: faker.commerce.productName(),
    price: faker.datatype.number(),
  };
});

export const cartProductFactory = Factory.define<CartProduct>(() => {
  return {
    product: productFactory.build(),
    quantity: faker.datatype.number({ min: 1, max: 999 }),
    total_price: faker.datatype.number({ min: 0 }),
  };
});

export const cartFactory = Factory.define<Cart>(() => {
  return {
    items: cartProductFactory.buildList(3),
    total_price: faker.datatype.number({ min: 0 }),
  };
});

export const storeVisitFactory = Factory.define<StoreVisit>(({ params }) => {
  const id = params.id ?? faker.datatype.uuid();
  return {
    self: `http://localhost/api/v1/storevisits/${id}`,
    id,
    store: storeUrl(faker.datatype.uuid()),
    cart: cartFactory.build(),
  };
});

export const groupedCartFactory = Factory.define<GroupedCart>(() => {
  return {
    binned_cart: cartFactory.buildList(3),
  };
});
