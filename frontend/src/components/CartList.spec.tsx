import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { faker } from "@faker-js/faker";

import { cartProductFactory } from "../test/factories";

import CartList from "./CartList";

const cart = cartProductFactory.buildList(3);
const totalPrice = faker.datatype.number({ min: 1 });

describe("CartList", () => {
  let onChangeQuantity: jest.Mock;

  beforeEach(() => {
    onChangeQuantity = jest.fn();
    render(
      <CartList
        cart={cart}
        totalPrice={totalPrice}
        onChangeQuantity={onChangeQuantity}
      />
    );
  });

  afterEach(() => {
    onChangeQuantity.mockRestore();
  });

  it("displays product info", () => {
    cart.forEach((cartProduct) =>
      expect(screen.getByText(cart[0].product.name)).toBeInTheDocument()
    );
  });

  it("displays total price", () => {
    expect(screen.getByText(String(totalPrice))).toBeInTheDocument();
  });

  it("supports changing quantity of item", async () => {
    const inputs = screen.getAllByRole("spinbutton");
    // make each quantity tenfold by appending 0
    await Promise.all(
      inputs.map(async (input) => {
        await userEvent.type(input, "0");
      })
    );
    cart.forEach((cartProduct, index) => {
      expect(onChangeQuantity).toHaveBeenCalledWith(
        index,
        10 * cartProduct.quantity
      );
    });
  });
});
