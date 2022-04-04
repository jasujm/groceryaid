import React from "react";
import Alert from "react-bootstrap/Alert";
import { Navigate } from "react-router-dom";

import { useSelector } from "../hooks";

export default function HomeView() {
  const storeVisit = useSelector((state) => state.storeVisit);

  return (
    <div className="home-view">
      {storeVisit ? (
        <Navigate to={`/storevisits/${storeVisit.id}`} replace={true} />
      ) : (
        <Alert variant="info">Select store to continue</Alert>
      )}
    </div>
  );
}
