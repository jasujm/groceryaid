import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import {
  createStoreVisit as apiCreateStoreVisit,
  getStoreVisit as apiGetStoreVisit,
  updateStoreVisit as apiUpdateStoreVisit,
  StoreVisit,
} from "../api";

export interface StoreVisitUpdate {
  storeVisit: StoreVisit;
  patch: unknown;
}

export const createStoreVisit = createAsyncThunk(
  "storeVisit/createStoreVisit",
  async (store: string) => {
    return await apiCreateStoreVisit(store);
  }
);

export const loadStoreVisit = createAsyncThunk(
  "storeVisit/loadStoreVisit",
  async (storeVisit: string) => {
    return await apiGetStoreVisit(storeVisit);
  }
);

export const updateStoreVisit = createAsyncThunk(
  "storeVisit/updateStoreVisit",
  async ({ storeVisit, patch }: StoreVisitUpdate) => {
    return await apiUpdateStoreVisit(storeVisit, patch);
  }
);

export const storeVisitSlice = createSlice({
  name: "storeVisit",
  initialState: null as StoreVisit | null,
  reducers: {
    clear: () => null,
  },
  extraReducers: (builder) => {
    builder.addCase(createStoreVisit.fulfilled, (state, action) => {
      return action.payload;
    });
    builder.addCase(loadStoreVisit.fulfilled, (state, action) => {
      return action.payload;
    });
    builder.addCase(updateStoreVisit.fulfilled, (state, action) => {
      return action.payload;
    });
  },
});

export default storeVisitSlice.reducer;

export const { clear } = storeVisitSlice.actions;
