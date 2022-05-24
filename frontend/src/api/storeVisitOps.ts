// Return update patches for several store visit operations
// Might consider to strongly type these or use some JSON patch library?

import { isVariablePriceEan } from "../ean";

export function addProduct(ean: string, quantity: number = 1) {
  return [
    {
      op: "add",
      path: "/cart/items/-",
      value: {
        product: ean,
        quantity: isVariablePriceEan(ean) ? undefined : quantity,
      },
    },
  ];
}

export function changeCartProductQuantity(index: number, quantity: number) {
  return [
    {
      op: "replace",
      path: `/cart/items/${index}/quantity`,
      value: quantity,
    },
  ];
}
