import React from "react";
import Form from "react-bootstrap/Form";
import Table from "react-bootstrap/Table";
import debounce from "lodash/debounce";

import { CartProduct } from "../api";

interface QuantityInputProps {
  value: number;
  onChange: (value: number) => void;
}

export interface Props {
  cart: readonly CartProduct[];
  totalPrice?: number;
  onChangeQuantity?: (index: number, quantity: number) => void;
}

function QuantityInput({ value, onChange }: QuantityInputProps) {
  const [uncommitedValue, setUncommitedValue] = React.useState<
    number | undefined
  >(undefined);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedOnChange = React.useCallback(debounce(onChange, 200), []);
  React.useEffect(() => {
    setUncommitedValue(undefined);
    debouncedOnChange.cancel();
  }, [value, debouncedOnChange]);
  function handleOnChange(value: number) {
    setUncommitedValue(value);
    debouncedOnChange(value);
  }
  return (
    <Form.Control
      className="quantity-input"
      type="number"
      min="1"
      value={uncommitedValue ?? value}
      onChange={(event) => handleOnChange(Number(event.target.value))}
    />
  );
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
                <QuantityInput
                  value={cartProduct.quantity}
                  onChange={(quantity) => onChangeQuantity?.(index, quantity)}
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
