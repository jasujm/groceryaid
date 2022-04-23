import { render, screen, act, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import * as api from "../api";
import { storeFactory, productFactory, cartFactory } from "../test/factories";

import CartEditor from "./CartEditor";

jest.mock("./../api");

const store = storeFactory.build();
const product = productFactory.build({ store: store.self });
const ean = product.ean;
const cart = cartFactory.build();

describe("CartEditor", () => {
  let onAddProduct: jest.Mock;
  let onChangeQuantity: jest.Mock;
  const getProduct = api.getProduct as jest.MockedFn<typeof api.getProduct>;

  beforeEach(() => {
    getProduct.mockResolvedValue(product);
    onAddProduct = jest.fn();
    onAddProduct.mockResolvedValue(undefined);
    onChangeQuantity = jest.fn();
    render(
      <CartEditor
        store={store.self}
        cart={cart}
        onAddProduct={onAddProduct}
        onChangeQuantity={onChangeQuantity}
      />
    );
  });

  afterEach(() => {
    getProduct.mockRestore();
  });

  it("renders products", () => {
    cart.items.forEach((item) => {
      expect(screen.getByText(item.product.name)).toBeInTheDocument();
    });
  });

  it("supports adding products", async () => {
    const input = screen.getByPlaceholderText(/ean/i) as HTMLInputElement;
    await act(() => userEvent.type(input, ean));
    const button = screen.getByRole("button");
    await act(() => userEvent.click(button));
    expect(onAddProduct).toHaveBeenCalledWith(ean);
  });

  it("supports changing quantities", async () => {
    const input = screen.getAllByRole("spinbutton")[0];
    await act(() => userEvent.type(input, "0"));
    await waitFor(
      () => {
        expect(onChangeQuantity).toHaveBeenCalled();
      },
      { timeout: 300 }
    );
  });
});
