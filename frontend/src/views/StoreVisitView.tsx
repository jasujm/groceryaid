import React from "react";
import { useParams } from "react-router-dom";
import Alert from "react-bootstrap/Alert";
import Tabs from "react-bootstrap/Tabs";
import Tab from "react-bootstrap/Tab";

import { useSelector, useDispatch } from "../hooks";
import { loadStoreVisit, updateStoreVisit } from "../reducers/storevisit";
import {
  addProduct,
  changeCartProductQuantity,
  removeProduct,
} from "../api/storeVisitOps";
import { getGroupedStoreVisitCart, GroupedCart } from "../api";
import CartEditor from "../components/CartEditor";
import GroupedCartDisplay from "../components/GroupedCart";

export default function StoreVisitView() {
  const storeVisit = useSelector((state) => state.storeVisit);
  const { id } = useParams();
  const dispatch = useDispatch();
  const [groupedCart, setGroupedCart] = React.useState<GroupedCart | null>(
    null
  );
  const [errorMessage, setErrorMessage] = React.useState("");

  function dispatchUpdateStoreVisit(patch: unknown) {
    // TODO: display errors for failed updates
    if (storeVisit) {
      return dispatch(updateStoreVisit({ storeVisit, patch })).unwrap();
    }
    return Promise.resolve();
  }

  async function onAddProduct(ean: string) {
    await dispatchUpdateStoreVisit(addProduct(ean));
  }

  async function onChangeQuantity(index: number, quantity: number) {
    await dispatchUpdateStoreVisit(changeCartProductQuantity(index, quantity));
  }

  async function onRemoveProduct(index: number) {
    await dispatchUpdateStoreVisit(removeProduct(index));
  }

  function loadGroupedCart() {
    if (storeVisit) {
      getGroupedStoreVisitCart(storeVisit.self).then(setGroupedCart);
    }
  }

  React.useEffect(() => {
    setErrorMessage("");
    if (id !== storeVisit?.id) {
      dispatch(loadStoreVisit(id!))
        .unwrap()
        .catch(() => {
          setErrorMessage("Store visit not found");
        });
    }
  }, [storeVisit, id, dispatch]);

  return (
    <div className="store-visit-view">
      {storeVisit && (
        <Tabs defaultActiveKey="cart-editor">
          <Tab eventKey="cart-editor" title="Cart">
            <CartEditor
              store={storeVisit.store}
              cart={storeVisit.cart}
              onAddProduct={onAddProduct}
              onChangeQuantity={onChangeQuantity}
              onRemoveProduct={onRemoveProduct}
            />
          </Tab>
          <Tab
            eventKey="cart-groups"
            title="Show grouped"
            onEnter={loadGroupedCart}
          >
            {groupedCart && <GroupedCartDisplay groupedCart={groupedCart} />}
          </Tab>
        </Tabs>
      )}
      {errorMessage && <Alert variant="warning">{errorMessage}</Alert>}
    </div>
  );
}
