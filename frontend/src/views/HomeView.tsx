import React from "react";
import Alert from "react-bootstrap/Alert";
import { Navigate } from "react-router-dom";

import { useSelector } from "../hooks";

export default function HomeView() {
  const storeVisit = useSelector((state) => state.storeVisit);

  if (storeVisit) {
    return <Navigate to={`/storevisits/${storeVisit.id}`} replace={true} />;
  } else {
    return <Alert variant="info">Select store to continue</Alert>;
  }
}
