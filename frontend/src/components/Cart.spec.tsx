import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { cartFactory } from "../test/factories";

import Cart from "./Cart";

const cart = cartFactory.build();

describe("Cart", () => {
  describe("when editable", () => {
    let onChangeQuantity: jest.Mock;
    let onRemoveProduct: jest.Mock;

    beforeEach(() => {
      onChangeQuantity = jest.fn();
      onRemoveProduct = jest.fn();
      render(
        <Cart
          cart={cart}
          onChangeQuantity={onChangeQuantity}
          onRemoveProduct={onRemoveProduct}
        />
      );
    });

    afterEach(() => {
      onChangeQuantity.mockRestore();
    });

    it("displays product info", () => {
      cart.items.forEach((item) =>
        expect(screen.getByText(item.product.name)).toBeInTheDocument()
      );
    });

    it("displays total price", () => {
      expect(screen.getByText(String(cart.total_price))).toBeInTheDocument();
    });

    it("supports changing quantity of item", async () => {
      const inputs = screen.getAllByRole("spinbutton");
      // make each quantity tenfold by appending 0
      await Promise.all(
        inputs.map(async (input) => {
          await userEvent.type(input, "0");
        })
      );
      await waitFor(
        () => {
          cart.items.forEach((item, index) => {
            expect(onChangeQuantity).toHaveBeenCalledWith(
              index,
              10 * item.quantity!
            );
          });
        },
        { timeout: 300 }
      );
    });

    it("supports removing products", async () => {
      const inputs = screen.getAllByRole("button");
      await Promise.all(
        inputs.map(async (input) => {
          await userEvent.click(input);
        })
      );
      cart.items.forEach((_, index) => {
        expect(onRemoveProduct).toHaveBeenCalledWith(index);
      });
    });
  });

  it("is optionally not editable", () => {
    render(<Cart cart={cart} editable={false} />);
    expect(screen.queryByRole("spinbutton")).not.toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });
});
