import React from "react";

import { StoreVisit } from "../api";

export interface Props {
  storeVisit?: StoreVisit;
}

export default function StoreVisitView({ storeVisit }: Props) {
  return <pre>{JSON.stringify(storeVisit, null, 2)}</pre>;
}
