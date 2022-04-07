// Return update patches for several store visit operations
// Might consider to strongly type these or use some JSON patch library?

export function addProduct(ean: string, quantity: number = 1) {
  return [
    {
      op: "add",
      path: "/cart/-",
      value: {
        product: ean,
        quantity,
      },
    },
  ];
}

export function changeCartProductQuantity(index: number, quantity: number) {
  return [
    {
      op: "replace",
      path: `/cart/${index}/quantity`,
      value: quantity,
    },
  ];
}
