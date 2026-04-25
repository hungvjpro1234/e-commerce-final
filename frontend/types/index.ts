export interface Category {
  id: number;
  name: string;
}

export interface BookDetail {
  author: string;
  publisher: string;
  isbn: string;
}

export interface ElectronicsDetail {
  brand: string;
  warranty: number;
}

export interface FashionDetail {
  size: string;
  color: string;
}

export interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
  category: number;
  category_data?: Category;
  detail_type?: "book" | "electronics" | "fashion";
  book?: BookDetail;
  electronics?: ElectronicsDetail;
  fashion?: FashionDetail;
}

export interface CartItem {
  id: number;
  product_id: number;
  quantity: number;
}

export interface Cart {
  id: number;
  user_id: number;
  items: CartItem[];
}

export interface UserRecord {
  id: number;
  username: string;
  email: string;
  role: string;
  first_name: string;
  last_name: string;
}

export interface Order {
  id: number;
  user_id: number;
  total_price: number;
  status: string;
  items: CartItem[];
}

export interface Shipment {
  id: number;
  order_id: number;
  user_id: number;
  address: string;
  status: string;
}

export interface PaymentStatus {
  id: number;
  order_id: number;
  user_id: number;
  amount: number;
  status: string;
}

export interface ProductFormValues {
  name: string;
  price: number;
  stock: number;
  category: number;
  detail_type: "book" | "electronics" | "fashion";
  detail: Record<string, string | number>;
}

export interface CategoryFormValues {
  name: string;
}

export interface UserFormValues {
  username: string;
  email: string;
  password?: string;
  role: "admin" | "staff" | "customer";
  first_name: string;
  last_name: string;
}
