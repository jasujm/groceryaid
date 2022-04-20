import React from "react";
import { Provider } from "react-redux";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import * as reactRouter from "react-router-dom";

import { storeVisitFactory, cartProductFactory } from "../test/factories";
import reduxStore from "../store";
import * as api from "../api";

import StoreVisitView from "./StoreVisitView";

jest.mock("../api");
jest.mock("react-router-dom");

describe("StoreVisitView", () => {
  let storeVisit: api.StoreVisit;
  const getStoreVisit = api.getStoreVisit as jest.MockedFn<
    typeof api.getStoreVisit
  >;
  const useParams = reactRouter.useParams as jest.MockedFn<
    typeof reactRouter.useParams
  >;

  function renderView() {
    render(
      <Provider store={reduxStore}>
        <StoreVisitView />
      </Provider>
    );
  }

  beforeEach(() => {
    storeVisit = storeVisitFactory.build();
    useParams.mockReturnValue({ id: storeVisit.id });
  });

  afterEach(() => {
    useParams.mockRestore();
    getStoreVisit.mockRestore();
  });

  describe("when store visit exists", () => {
    beforeEach(async () => {
      getStoreVisit.mockResolvedValue(storeVisit);
      await act(() => renderView());
    });

    it("loads store visit", () => {
      expect(api.getStoreVisit).toHaveBeenCalledWith(storeVisit.id);
    });

    it("adds products", async () => {
      const updatedStoreVisit = {
        ...storeVisit,
        cart: {
          ...storeVisit.cart,
          items: [...storeVisit.cart.items, cartProductFactory.build()],
        },
      };
      const updateStoreVisit = api.updateStoreVisit as jest.MockedFn<
        typeof api.updateStoreVisit
      >;
      updateStoreVisit.mockResolvedValueOnce(updatedStoreVisit);
      const input = screen.getByPlaceholderText(/ean/i);
      await userEvent.type(input, updatedStoreVisit.cart.items[0].product.ean);
      const button = screen.getByRole("button");
      await act(() => userEvent.click(button));
      expect(updateStoreVisit).toHaveBeenCalled();
    });
  });

  describe("when store visit does not exist", () => {
    it("displays error", async () => {
      getStoreVisit.mockRejectedValue(undefined);
      await act(() => renderView());
      const errorMessage = await screen.findByText(/not found/i);
      expect(errorMessage).toBeInTheDocument();
    });
  });
});
