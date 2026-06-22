// ── Auth ──────────────────────────────────────────────────────────────
export interface User {
  id: number;
  username: string;
  email: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// ── Products ──────────────────────────────────────────────────────────
export interface Category {
  id: number;
  name: string;
  description?: string;
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  price: number;
  stock: number;
  is_active: boolean;
  category_id: number;
  category: Category;
}

export interface ProductListResponse {
  total: number;
  page: number;
  page_size: number;
  results: Product[];
}

export interface ProductFilters {
  page?: number;
  page_size?: number;
  search?: string;
  category_id?: number;
  min_price?: number;
  max_price?: number;
}

// ── Cart ──────────────────────────────────────────────────────────────
export interface CartItem {
  product_id: number;
  name: string;
  price: number;
  quantity: number;
  subtotal: number;
}

export interface Cart {
  user_id: string;
  items: CartItem[];
  total_items: number;
  total_price: number;
  ttl_seconds?: number;
}

// ── Orders ────────────────────────────────────────────────────────────
export type OrderStatus =
  | "PENDING"
  | "CONFIRMED"
  | "SHIPPED"
  | "DELIVERED"
  | "CANCELLED"
  | "FAILED";

export interface OrderItem {
  id: number;
  product_id: number;
  name: string;
  price: number;
  quantity: number;
  subtotal: number;
}

export interface Order {
  id: number;
  user_id: string;
  status: OrderStatus;
  total_price: number;
  created_at: string;
  updated_at?: string;
  items: OrderItem[];
}

export interface OrderListResponse {
  total: number;
  page: number;
  page_size: number;
  results: Order[];
}

// ── Payments ──────────────────────────────────────────────────────────
export type PaymentStatus =
  | "CREATED"
  | "SUCCESS"
  | "FAILED"
  | "REFUNDED"
  | "PARTIAL_REFUND";

export interface Payment {
  id: number;
  order_id: number;
  user_id: string;
  amount: number;
  currency: string;
  status: PaymentStatus;
  razorpay_order_id: string;
  razorpay_payment_id?: string;
  refund_id?: string;
  refunded_amount?: number;
  created_at: string;
}

export interface CreatePaymentResponse {
  payment_id: number;
  razorpay_order_id: string;
  razorpay_key_id: string;
  amount: number;
  currency: string;
}