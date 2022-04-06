import React from "react";
import Table from "react-bootstrap/Table";

import { CartProduct } from "../api";

export interface Props {
  cart: readonly CartProduct[];
}

export default function CartList({ cart }: Props) {
  return (
    <div className="cart-list">
      <Table className="cart-list-table">
        <thead>
          <tr>
            <th>Product</th>
            <th>EAN code</th>
            <th>Quantity</th>
            <th>Total price</th>
          </tr>
        </thead>
        <tbody>
          {cart.map((cartProduct) => (
            <tr key={cartProduct.product.self}>
              <td>{cartProduct.product.name}</td>
              <td>{cartProduct.product.ean}</td>
              <td>{cartProduct.quantity}</td>
              <td>{cartProduct.total_price}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}
