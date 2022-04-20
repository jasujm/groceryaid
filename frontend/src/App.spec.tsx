import React from "react";
import { Provider } from "react-redux";
import { Router } from "react-router-dom";
import { render, screen, act, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createMemoryHistory, MemoryHistory } from "history";

import App from "./App";
import reduxStore from "./store";
import * as api from "./api";
import { storeFactory, storeVisitFactory } from "./test/factories";

jest.mock("./api");

const stores = storeFactory.buildList(3);
const store = stores[0];

describe("App", () => {
  let history: MemoryHistory;
  const getStores = api.getStores as jest.MockedFn<typeof api.getStores>;

  function renderApp() {
    render(
      <Provider store={reduxStore}>
        <Router location={history.location} navigator={history}>
          <App />
        </Router>
      </Provider>
    );
  }

  beforeEach(() => {
    history = createMemoryHistory();
    getStores.mockResolvedValue(stores);
  });

  afterEach(() => {
    getStores.mockRestore();
  });

  it("creates store visit when store is selected", async () => {
    const storeVisit = storeVisitFactory.build({ store: store.self });
    const createStoreVisit = api.createStoreVisit as jest.MockedFn<
      typeof api.createStoreVisit
    >;
    await act(async () => renderApp());
    await waitFor(() => expect(getStores).toHaveBeenCalled());
    const user = userEvent.setup();
    createStoreVisit.mockResolvedValueOnce(storeVisit);
    const select = screen.getByRole("combobox");
    await act(() => user.selectOptions(select, store.name));
    expect(createStoreVisit).toHaveBeenCalledWith(store.self);
    expect(history.location.pathname).toEqual(`/storevisits/${storeVisit.id}`);
  });

  it("does not create store visit when empty option is selected", async () => {
    const createStoreVisit = api.createStoreVisit as jest.MockedFn<
      typeof api.createStoreVisit
    >;
    await act(async () => renderApp());
    await waitFor(() => expect(getStores).toHaveBeenCalled());
    const user = userEvent.setup();
    const select = screen.getByRole("combobox");
    await act(() => user.selectOptions(select, ""));
    expect(createStoreVisit).not.toHaveBeenCalled();
  });

  it("loads store visit when navigating to page", async () => {
    const storeVisit = storeVisitFactory.build({ store: store.self });
    const getStoreVisit = api.getStoreVisit as jest.MockedFn<
      typeof api.getStoreVisit
    >;
    getStoreVisit.mockResolvedValue(storeVisit);
    history.push(`/storevisits/${storeVisit.id}`);
    await act(async () => renderApp());
    await waitFor(() => expect(getStores).toHaveBeenCalled());
    expect(api.getStoreVisit).toHaveBeenCalled();
    expect(screen.getByText(store.name)).toBeInTheDocument();
  });
});
