import React from "react";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import ProductPicker from "./ProductPicker";

const ean = "1234567890123";

describe("ProductPicker", () => {
  let onAddProduct: jest.Mock;

  beforeEach(() => {
    onAddProduct = jest.fn();
    render(<ProductPicker onAddProduct={onAddProduct} />);
  });

  it("dispatches add product event", async () => {
    onAddProduct.mockResolvedValue(undefined);
    const input = screen.getByPlaceholderText(/ean/i) as HTMLInputElement;
    await userEvent.type(input, ean);
    const button = screen.getByRole("button");
    await act(() => userEvent.click(button));
    expect(onAddProduct).toHaveBeenCalledWith(ean);
    expect(input.value).toBeFalsy();
  });

  it("does not clear input on error", async () => {
    onAddProduct.mockRejectedValue(new Error("error"));
    const input = screen.getByPlaceholderText(/ean/i) as HTMLInputElement;
    await userEvent.type(input, ean);
    const button = screen.getByRole("button");
    await act(() => userEvent.click(button));
    expect(onAddProduct).toHaveBeenCalledWith(ean);
    expect(input.value).toEqual(ean);
  });
});
