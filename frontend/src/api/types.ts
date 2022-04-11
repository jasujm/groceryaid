export interface Store {
  self: string;
  id: string;
  name: string;
}

export interface Product {
  self: string;
  store: string;
  ean: string;
  name: string;
  price: number;
}

export interface CartProduct {
  product: Product;
  quantity: number;
  total_price: number;
}

export interface Cart {
  items: CartProduct[];
  total_price: number;
}

export interface StoreVisit {
  self: string;
  id: string;
  store: string;
  cart: Cart;
}
