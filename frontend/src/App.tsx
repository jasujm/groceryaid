import React from "react";
import Alert from "react-bootstrap/Alert";
import Container from "react-bootstrap/Container";
import { Routes, Route, useNavigate, useLocation } from "react-router-dom";

import StoreVisitView from "./views/StoreVisitView";
import StorePicker from "./components/StorePicker";
import { createStoreVisit, getStoreVisit, StoreVisit } from "./api";

import "./App.scss";

const STORE_VISIT_URL_RE = /\/storevisits\/(?<id>[0-9a-f-]+)$/;

function getIdFromStoreVisitUrl(storeVisitUrl: string) {
  const match = storeVisitUrl.match(STORE_VISIT_URL_RE);
  return match?.groups?.id;
}

export default function App() {
  const [storeVisit, setStoreVisit] = React.useState<StoreVisit | undefined>(
    undefined
  );
  const navigate = useNavigate();
  const location = useLocation();

  React.useEffect(() => {
    const storeVisitId = getIdFromStoreVisitUrl(location.pathname);
    if (storeVisitId) {
      getStoreVisit(storeVisitId).then(setStoreVisit);
    }
  }, [location]);

  function onStoreSelected(store: string) {
    createStoreVisit(store).then((newStoreVisit) => {
      setStoreVisit(newStoreVisit);
      navigate(`/storevisits/${newStoreVisit.id}`, { replace: true });
    });
  }

  return (
    <Container id="app">
      <h1>Grocery Aid</h1>
      <StorePicker onChange={onStoreSelected} value={storeVisit?.store} />
      <Routes>
        <Route
          index
          element={<Alert variant="info">Select store to continue</Alert>}
        />
        <Route
          path="/storevisits/:id"
          element={<StoreVisitView storeVisit={storeVisit} />}
        />
      </Routes>
    </Container>
  );
}
