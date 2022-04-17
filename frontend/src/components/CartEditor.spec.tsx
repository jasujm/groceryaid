import { render, screen, act, waitFor } from "@testing-library/react";
import { cartFactory } from "../test/factories";
import userEvent from "@testing-library/user-event";

import CartEditor from "./CartEditor";

const cart = cartFactory.build();
const ean = "1234567890123";

describe("CartEditor", () => {
  let onAddProduct: jest.Mock;
  let onChangeQuantity: jest.Mock;

  beforeEach(() => {
    onAddProduct = jest.fn();
    onAddProduct.mockResolvedValue(undefined);
    onChangeQuantity = jest.fn();
    render(
      <CartEditor
        cart={cart}
        onAddProduct={onAddProduct}
        onChangeQuantity={onChangeQuantity}
      />
    );
  });

  it("renders products", () => {
    cart.items.forEach((item) => {
      expect(screen.getByText(item.product.name)).toBeInTheDocument();
    });
  });

  it("supports adding products", async () => {
    const input = screen.getByPlaceholderText(/ean/i) as HTMLInputElement;
    await userEvent.type(input, ean);
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
