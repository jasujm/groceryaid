import React from "react";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import * as api from "../api";
import { storeFactory, productFactory } from "../test/factories";

import ProductPicker from "./ProductPicker";

jest.mock("./../api");

const store = storeFactory.build();
const product = productFactory.build({ store: store.self });
const ean = product.ean;

describe("ProductPicker", () => {
  let onAddProduct: jest.Mock;
  const getProduct = api.getProduct as jest.MockedFn<typeof api.getProduct>;

  beforeEach(() => {
    getProduct.mockResolvedValue(product);
    onAddProduct = jest.fn();
    render(<ProductPicker store={store.self} onAddProduct={onAddProduct} />);
  });

  afterEach(() => {
    getProduct.mockRestore();
  });

  async function typeEan(ean: string) {
    const input = screen.getByPlaceholderText(/ean/i) as HTMLInputElement;
    await act(() => userEvent.type(input, ean));
  }

  it("dispatches add product event", async () => {
    onAddProduct.mockResolvedValue(undefined);
    await typeEan(ean);
    const submit = screen.getByLabelText(/add product/i);
    await act(() => userEvent.click(submit));
    expect(onAddProduct).toHaveBeenCalledWith(ean);
  });

  it("validates ean", async () => {
    await typeEan("invalid");
    const error = await screen.findByText(/invalid ean/i);
    expect(error).toBeInTheDocument();
    const submit = screen.getByLabelText(/add product/i);
    expect(submit).toBeDisabled();
  });

  it("displays product", async () => {
    await typeEan(ean);
    const productName = await screen.findByText(product.name);
    expect(productName).toBeInTheDocument();
  });

  it("displays error on nonexisting product", async () => {
    getProduct.mockRejectedValue(new Error("no product"));
    await typeEan(ean);
    const error = await screen.findByText(/no product/i);
    expect(error).toBeInTheDocument();
  });

  it("does not clear input on error", async () => {
    onAddProduct.mockRejectedValue(new Error("bad error"));
    const input = screen.getByPlaceholderText(/ean/i) as HTMLInputElement;
    await act(() => userEvent.type(input, ean));
    const submit = screen.getByLabelText(/add product/i);
    await act(() => userEvent.click(submit));
    expect(onAddProduct).toHaveBeenCalledWith(ean);
    expect(input.value).toEqual(ean);
    const error = screen.getByText(/bad error/i);
    expect(error).toBeInTheDocument();
  });

  it("renders barcode scanner", async () => {
    const button = screen.getByLabelText(/scan/i);
    await act(() => userEvent.click(button));
    const modal = screen.getByText(/scan barcode/i);
    expect(modal).toBeInTheDocument();
  });
});
