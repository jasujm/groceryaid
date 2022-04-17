import React from "react";

import { GroupedCart } from "../api";

import Cart from "./Cart";

export interface Props {
  groupedCart: GroupedCart;
}

export default function GroupedCartDisplay({ groupedCart }: Props) {
  return (
    <div className="grouped-cart">
      {groupedCart.binned_cart.map((cart, index) => (
        <div key={index} className="cart-group">
          <strong>Group {index + 1}</strong>
          <Cart cart={cart} editable={false} />
        </div>
      ))}
    </div>
  );
}
