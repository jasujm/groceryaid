import React from "react";
import { useParams } from "react-router-dom";
import Tabs from "react-bootstrap/Tabs";
import Tab from "react-bootstrap/Tab";

import { useSelector, useDispatch } from "../hooks";
import { loadStoreVisit, updateStoreVisit } from "../reducers/storevisit";
import { addProduct, changeCartProductQuantity } from "../api/storeVisitOps";
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

  function loadGroupedCart() {
    if (storeVisit) {
      getGroupedStoreVisitCart(storeVisit.self).then(setGroupedCart);
    }
  }

  React.useEffect(() => {
    if (id !== storeVisit?.id) {
      dispatch(loadStoreVisit(id!));
    }
  }, [storeVisit, id, dispatch]);

  return (
    storeVisit && (
      <Tabs className="store-visit-view" defaultActiveKey="cart-editor">
        <Tab eventKey="cart-editor" title="Cart">
          <CartEditor
            cart={storeVisit.cart}
            onAddProduct={onAddProduct}
            onChangeQuantity={onChangeQuantity}
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
    )
  );
}
