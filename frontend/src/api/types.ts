export interface Store {
  self: string;
  id: string;
  name: string;
}

export interface CartProduct {
  product: string;
  quantity: number;
}

export interface StoreVisit {
  self: string;
  id: string;
  store: string;
  cart: CartProduct[];
}
