import React, { FormEvent } from "react";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import InputGroup from "react-bootstrap/InputGroup";

export interface Props {
  onAddProduct?: (ean: string) => void;
}

export default function ProductPicker({ onAddProduct }: Props) {
  const [ean, setEan] = React.useState("");

  function addProduct(event: FormEvent) {
    event.preventDefault();
    if (onAddProduct) {
      onAddProduct(ean);
      setEan("");
    }
  }

  return (
    <div className="product-picker">
      <Form onSubmit={addProduct}>
        <InputGroup>
          <Form.Control
            placeholder="EAN Code"
            value={ean}
            onChange={(event) => setEan(event.target.value)}
          />
          <Button type="submit">Add product</Button>
        </InputGroup>
      </Form>
    </div>
  );
}
