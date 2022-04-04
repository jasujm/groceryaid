import { configureStore } from "@reduxjs/toolkit";

import storeVisitReducer from "./reducers/storevisit";

const store = configureStore({
  reducer: {
    storeVisit: storeVisitReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export default store;
