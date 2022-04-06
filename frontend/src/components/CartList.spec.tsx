import React from "react";
import { render, screen } from "@testing-library/react";

import { cartProductFactory } from "../test/factories";

import CartList from "./CartList";

const cart = cartProductFactory.buildList(3);

describe("CartList", () => {
  it("displays product info", () => {
    render(<CartList cart={cart} />);
    cart.forEach((cartProduct) =>
      expect(screen.getByText(cart[0].product.name)).toBeInTheDocument()
    );
  });
});
