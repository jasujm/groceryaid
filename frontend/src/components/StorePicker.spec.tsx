import React from "react";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import StorePicker from "./StorePicker";
import * as api from "../api";

jest.mock("../api");

const store = {
  id: "16c5b78c-190f-4172-a424-b566396324e8",
  self: "/stores/16c5b78c-190f-4172-a424-b566396324e8",
  name: "The Shop",
};

describe("StorePicker", () => {
  let getStores = api.getStores as jest.MockedFn<typeof api.getStores>;
  let onChange: jest.Mock;

  beforeEach(() => {
    getStores.mockResolvedValue([store]);
    onChange = jest.fn();
  });

  afterEach(() => {
    getStores.mockRestore();
  });

  describe("when no store is selected", () => {
    beforeEach(async () => {
      await act(async () => {
        render(<StorePicker onChange={onChange} />);
      });
    });

    it("displays no store", async () => {
      const select = await screen.findByDisplayValue(/select store/i);
      expect(select).not.toBeUndefined();
    });

    it("invokes callback on store select", async () => {
      const user = userEvent.setup();
      const select = await screen.findByRole("combobox");
      await act(async () => {
        await user.selectOptions(select, store.name);
      });
      expect(onChange).toHaveBeenCalledWith(store.self);
    });
  });

  describe("when store is selected", () => {
    beforeEach(async () => {
      await act(async () => {
        render(<StorePicker value={store.self} onChange={onChange} />);
      });
    });

    it("displays selected store", async () => {
      const select = await screen.findByDisplayValue(store.name);
      expect(select).not.toBeUndefined();
    });

    it("is disabled", async () => {
      const select = (await screen.findByRole("combobox")) as HTMLSelectElement;
      expect(select.disabled).toBeTruthy();
    });
  });
});
