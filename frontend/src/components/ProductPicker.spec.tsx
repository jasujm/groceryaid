import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import ProductPicker from "./ProductPicker";

const ean = "1234567890123";

describe("ProductPicker", () => {
  it("dispatches add product event", async () => {
    const onAddProduct = jest.fn();
    render(<ProductPicker onAddProduct={onAddProduct} />);
    const input = screen.getByPlaceholderText(/ean/i);
    expect(input).toBeInTheDocument();
    await userEvent.type(input, ean);
    const button = screen.getByRole("button");
    await userEvent.click(button);
    expect(onAddProduct).toHaveBeenCalledWith(ean);
  });
});
