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
