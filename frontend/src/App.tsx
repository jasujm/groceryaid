import React from "react";
import Container from "react-bootstrap/Container";
import { Routes, Route } from "react-router-dom";

import { useSelector, useDispatch } from "./hooks";
import HomeView from "./views/HomeView";
import StoreVisitView from "./views/StoreVisitView";
import StorePicker from "./components/StorePicker";
import { createStoreVisit } from "./reducers/storevisit";

import "./App.scss";

export default function App() {
  const storeVisit = useSelector((state) => state.storeVisit);
  const dispatch = useDispatch();

  function onStoreSelected(store: string) {
    dispatch(createStoreVisit(store));
  }

  return (
    <Container id="app">
      <h1>Grocery Aid</h1>
      <StorePicker onChange={onStoreSelected} value={storeVisit?.store} />
      <Routes>
        <Route index element={<HomeView />} />
        <Route path="/storevisits/:id" element={<StoreVisitView />} />
      </Routes>
    </Container>
  );
}
