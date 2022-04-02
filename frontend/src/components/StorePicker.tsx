import React from "react";
import Form from "react-bootstrap/Form";

import { Store, getStores } from "../api";

export interface Props {
  value?: string;
  onChange?: (value: string) => void;
}

export default function StorePicker({ value, onChange }: Props) {
  const [options, setOptions] = React.useState<Store[]>([]);

  React.useEffect(() => {
    getStores().then(setOptions);
  }, []);

  return (
    <Form.Select
      className="store-picker"
      value={value}
      disabled={Boolean(value)}
      onChange={(event) => onChange?.(event.target.value)}
    >
      <option>-- Select store --</option>
      {options.map((option) => (
        <option key={option.id} value={option.self}>
          {option.name}
        </option>
      ))}
    </Form.Select>
  );
}
