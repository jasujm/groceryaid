import React from "react";
import Alert from "react-bootstrap/Alert";
import Container from "react-bootstrap/Container";
import { Link, Routes, Route, useNavigate } from "react-router-dom";

import { useSelector, useDispatch } from "./hooks";
import HomeView from "./views/HomeView";
import StoreVisitView from "./views/StoreVisitView";
import StorePicker from "./components/StorePicker";
import { createStoreVisit, clear } from "./reducers/storevisit";

import "./App.scss";

export default function App() {
  const storeVisit = useSelector((state) => state.storeVisit);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  function onStoreSelected(store: string) {
    if (store) {
      // TODO: catch error on failed creation
      dispatch(createStoreVisit(store))
        .unwrap()
        .then((storeVisit) => {
          navigate(`/storevisits/${storeVisit.id}`, { replace: true });
        });
    }
  }

  function onNavigateHome() {
    dispatch(clear());
  }

  return (
    <Container id="app">
      <h1>
        <Link onClick={onNavigateHome} to="/">
          Grocery Aid
        </Link>
      </h1>
      <main>
        <StorePicker
          onChange={onStoreSelected}
          value={storeVisit ? storeVisit.store : ""}
        />
        <Routes>
          <Route index element={<HomeView />} />
          <Route path="/storevisits/:id" element={<StoreVisitView />} />
          <Route
            path="*"
            element={<Alert variant="warning">Nothing here ☹️</Alert>}
          />
        </Routes>
      </main>
      <footer className="fixed-bottom">
        <small>
          <strong>Disclaimed:</strong> Nothing is guaranteed, including but not
          limited to the accuracy of prices.
        </small>
      </footer>
    </Container>
  );
}
