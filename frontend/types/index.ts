import type { ProductDetailType, ProductDetailValue } from "@/lib/product-types";

export interface Category {
  id: number;
  name: string;
}

export interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
  category: number;
  category_data?: Category;
  detail_type: ProductDetailType | string;
  detail: Record<string, ProductDetailValue>;
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

export type BehaviorAction = "view" | "click" | "search" | "add_to_cart" | "buy";

export interface BehaviorEventPayload {
  user_id: number;
  action: BehaviorAction;
  product_id?: number;
  query_text?: string;
}

export interface RecommendationItem {
  id: number;
  name: string;
  price: number;
  category: string;
  detail_type: string;
  score: number;
  reason: string;
  source_scores: Record<string, number>;
}

export interface RecommendationResponse {
  user_id: number;
  query?: string | null;
  total: number;
  items: RecommendationItem[];
  sources_used: string[];
}

export interface ChatbotProductSuggestion {
  id: number;
  name: string;
  price: number;
  category: string;
  detail_type: string;
  score: number;
  reason: string;
}

export interface ChatbotResponse {
  answer: string;
  products: ChatbotProductSuggestion[];
  retrieved_context: string[];
  query_type: string;
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
  detail_type: ProductDetailType | string;
  detail: Record<string, ProductDetailValue>;
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
