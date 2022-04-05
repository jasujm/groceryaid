import { Factory } from "fishery";
import { faker } from "@faker-js/faker";

import { Store, StoreVisit } from "../api";

function storeUrl(storeId: string) {
  return `http://localhost/api/v1/stores/${storeId}`;
}

export const storeFactory = Factory.define<Store>(({ params }) => {
  const id = params.id ?? faker.datatype.uuid();
  return {
    self: storeUrl(id),
    id,
    name: faker.address.city(),
  };
});

export const storeVisitFactory = Factory.define<StoreVisit>(({ params }) => {
  const id = params.id ?? faker.datatype.uuid();
  return {
    self: `http://localhost/api/v1/storevisits/${id}`,
    id,
    store: storeUrl(faker.datatype.uuid()),
    cart: [],
  };
});
