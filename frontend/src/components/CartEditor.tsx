import ProductPicker, { Props as ProductPickerProps } from "./ProductPicker";
import Cart, { Props as CartProps } from "./Cart";

export interface Props {
  onAddProduct?: ProductPickerProps["onAddProduct"];
  onChangeQuantity?: CartProps["onChangeQuantity"];
  cart: CartProps["cart"];
}

export default function CartEditor({
  onAddProduct,
  onChangeQuantity,
  cart,
}: Props) {
  return (
    <div className="cart-editor">
      <ProductPicker onAddProduct={onAddProduct} />
      <Cart cart={cart} onChangeQuantity={onChangeQuantity} />
    </div>
  );
}
