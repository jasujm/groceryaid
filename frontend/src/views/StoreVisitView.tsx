import React from "react";
import { useParams } from "react-router-dom";

import { useSelector, useDispatch } from "../hooks";
import { loadStoreVisit, updateStoreVisit } from "../reducers/storevisit";
import { addProduct } from "../api/storeVisitOps";
import ProductPicker from "../components/ProductPicker";

export default function StoreVisitView() {
  const storeVisit = useSelector((state) => state.storeVisit);
  const { id } = useParams();
  const dispatch = useDispatch();

  function dispatchUpdateStoreVisit(patch: unknown) {
    if (storeVisit) {
      dispatch(updateStoreVisit({ storeVisit, patch }));
    }
  }

  async function onAddProduct(ean: string) {
    dispatchUpdateStoreVisit(addProduct(ean));
  }

  React.useEffect(() => {
    if (id !== storeVisit?.id) {
      dispatch(loadStoreVisit(id!));
    }
  }, [storeVisit, id, dispatch]);

  return (
    <div className="store-visit-view">
      <ProductPicker onAddProduct={onAddProduct} />
      <pre>{JSON.stringify(storeVisit, null, 2)}</pre>
    </div>
  );
}
