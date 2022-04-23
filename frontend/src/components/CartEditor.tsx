import ProductPicker, { Props as ProductPickerProps } from "./ProductPicker";
import Cart, { Props as CartProps } from "./Cart";

export interface Props {
  onAddProduct?: ProductPickerProps["onAddProduct"];
  onChangeQuantity?: CartProps["onChangeQuantity"];
  cart: CartProps["cart"];
  store: string;
}

export default function CartEditor({
  onAddProduct,
  onChangeQuantity,
  cart,
  store,
}: Props) {
  return (
    <div className="cart-editor">
      <ProductPicker store={store} onAddProduct={onAddProduct} />
      <Cart cart={cart} onChangeQuantity={onChangeQuantity} />
    </div>
  );
}
