import { render, screen } from "@testing-library/react";
import { groupedCartFactory } from "../test/factories";

import GroupedCart from "./GroupedCart";

const groupedCart = groupedCartFactory.build();

describe("GroupedCart", () => {
  it("renders carts", () => {
    render(<GroupedCart groupedCart={groupedCart} />);
    groupedCart.binned_cart.forEach((cart) => {
      cart.items.forEach((item) => {
        expect(screen.getByText(item.product.name)).toBeInTheDocument();
      });
    });
  });
});
