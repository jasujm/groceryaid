import React from "react";
import { useParams } from "react-router-dom";

import { useSelector, useDispatch } from "../hooks";
import { loadStoreVisit, updateStoreVisit } from "../reducers/storevisit";
import { addProduct, changeCartProductQuantity } from "../api/storeVisitOps";
import ProductPicker from "../components/ProductPicker";
import CartList from "../components/CartList";

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

  async function onChangeQuantity(index: number, quantity: number) {
    dispatchUpdateStoreVisit(changeCartProductQuantity(index, quantity));
  }

  React.useEffect(() => {
    if (id !== storeVisit?.id) {
      dispatch(loadStoreVisit(id!));
    }
  }, [storeVisit, id, dispatch]);

  return (
    <div className="store-visit-view">
      <ProductPicker onAddProduct={onAddProduct} />
      <CartList
        cart={storeVisit?.cart ?? []}
        totalPrice={storeVisit?.total_price}
        onChangeQuantity={onChangeQuantity}
      />
    </div>
  );
}
