import React from "react";
import { useParams } from "react-router-dom";

import { useSelector, useDispatch } from "../hooks";
import { loadStoreVisit } from "../reducers/storevisit";

export default function StoreVisitView() {
  const storeVisit = useSelector((state) => state.storeVisit);
  const { id } = useParams();
  const dispatch = useDispatch();

  React.useEffect(() => {
    if (id !== storeVisit?.id) {
      dispatch(loadStoreVisit(id!));
    }
  }, [storeVisit, id, dispatch]);

  return <pre>{JSON.stringify(storeVisit, null, 2)}</pre>;
}
