import React from "react";
import Form from "react-bootstrap/Form";
import Table from "react-bootstrap/Table";

import { CartProduct } from "../api";

export interface Props {
  cart: readonly CartProduct[];
  totalPrice?: number;
  onChangeQuantity?: (index: number, quantity: number) => void;
}

export default function CartList({
  cart,
  totalPrice,
  onChangeQuantity,
}: Props) {
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
          {cart.map((cartProduct, index) => (
            <tr key={cartProduct.product.self} className="cart-product">
              <td>{cartProduct.product.name}</td>
              <td>{cartProduct.product.ean}</td>
              <td>
                <Form.Control
                  type="number"
                  min="1"
                  value={cartProduct.quantity}
                  onChange={(event) =>
                    onChangeQuantity?.(index, Number(event.target.value))
                  }
                />
              </td>
              <td>{cartProduct.total_price}</td>
            </tr>
          ))}
          {totalPrice ? (
            <tr className="cart-total-price">
              <td colSpan={3}></td>
              <td>{totalPrice}</td>
            </tr>
          ) : undefined}
        </tbody>
      </Table>
    </div>
  );
}
