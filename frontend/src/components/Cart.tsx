import React from "react";
import Form from "react-bootstrap/Form";
import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";
import InputGroup from "react-bootstrap/InputGroup";
import { Trash } from "react-bootstrap-icons";
import debounce from "lodash/debounce";

import { Cart } from "../api";

interface QuantityInputProps {
  value: number;
  onChange: (value: number) => void;
}

export interface Props {
  cart: Cart;
  onChangeQuantity?: (index: number, quantity: number) => void;
  onRemoveProduct?: (index: number) => void;
  editable?: boolean;
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
      max="999"
      value={uncommitedValue ?? value}
      onChange={(event) => handleOnChange(Number(event.target.value))}
      aria-label="Change quantity"
    />
  );
}

export default function CartList({
  cart: { items, total_price: totalPrice },
  onChangeQuantity,
  onRemoveProduct,
  editable = true,
}: Props) {
  return (
    <div className="cart">
      <Table className="cart-table">
        <thead>
          <tr>
            <th>Product</th>
            <th>EAN Code</th>
            <th>Quantity</th>
            <th>Price</th>
          </tr>
        </thead>
        <tbody>
          {items.map((cartItem, index) => (
            <tr
              key={`${cartItem.product.ean}-${index}`}
              className="cart-product"
            >
              <td>{cartItem.product.name}</td>
              <td>{cartItem.product.ean}</td>
              <td>
                {editable ? (
                  <InputGroup>
                    {cartItem.quantity != null && (
                      <QuantityInput
                        value={cartItem.quantity}
                        onChange={(quantity) =>
                          onChangeQuantity?.(index, quantity)
                        }
                      />
                    )}
                    <Button
                      className="remove-product"
                      variant="danger"
                      onClick={() => onRemoveProduct?.(index)}
                      aria-label="Remove product"
                    >
                      <Trash />
                    </Button>
                  </InputGroup>
                ) : (
                  cartItem.quantity
                )}
              </td>
              <td>{cartItem.total_price}</td>
            </tr>
          ))}
          {totalPrice ? (
            <tr className="cart-total-price">
              <td colSpan={3}>Total</td>
              <td>{totalPrice}</td>
            </tr>
          ) : undefined}
        </tbody>
      </Table>
    </div>
  );
}
