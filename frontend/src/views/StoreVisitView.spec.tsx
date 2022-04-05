import React from "react";
import { Provider } from "react-redux";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import * as reactRouter from "react-router-dom";

import { storeVisitFactory } from "../test/factories";
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

  async function renderView() {
    render(
      <Provider store={reduxStore}>
        <StoreVisitView />
      </Provider>
    );
  }

  beforeEach(async () => {
    storeVisit = storeVisitFactory.build();
    useParams.mockReturnValue({ id: storeVisit.id });
    getStoreVisit.mockResolvedValue(storeVisit);
    await act(() => renderView());
  });

  afterEach(() => {
    useParams.mockRestore();
    getStoreVisit.mockRestore();
  });

  it("loads store visit", () => {
    expect(api.getStoreVisit).toHaveBeenCalledWith(storeVisit.id);
  });

  it("adds products", async () => {
    const ean = "1234567890123";
    const updatedStoreVisit = {
      ...storeVisit,
      cart: [
        ...storeVisit.cart,
        {
          product: `${storeVisit.store}/products/${ean}`,
          quantity: 1,
        },
      ],
    };
    const updateStoreVisit = api.updateStoreVisit as jest.MockedFn<
      typeof api.updateStoreVisit
    >;
    updateStoreVisit.mockResolvedValueOnce(updatedStoreVisit);
    const input = screen.getByPlaceholderText(/ean/i);
    await userEvent.type(input, ean);
    const button = screen.getByRole("button");
    await act(() => userEvent.click(button));
    expect(updateStoreVisit).toHaveBeenCalled();
  });
});
