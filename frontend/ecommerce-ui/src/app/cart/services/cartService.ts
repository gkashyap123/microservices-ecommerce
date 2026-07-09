import api from "../../core/api/axiosInstance";
import type { Cart } from "../../shared/types";

function ensureUserId(userId: string): string {
  if (!userId) {
    throw new Error("User ID is required for cart requests.");
  }
  return userId;
}

export const cartService = {
  getCart: async (_userId: string): Promise<Cart> => {
    // Gateway identifies user from the Authorization header; do not include user id in the path
    const res = await api.get(`/cart`);
    return res.data;
  },

  addItem: async (
    _userId: string,
    item: { product_id: number; name: string; price: number; quantity: number }
  ): Promise<Cart> => {
    const res = await api.post(`/cart/items`, item);
    return res.data;
  },

  updateItem: async (
    _userId: string,
    productId: number,
    quantity: number
  ): Promise<Cart> => {
    const res = await api.put(`/cart/items/${productId}`, { quantity });
    return res.data;
  },

  removeItem: async (_userId: string, productId: number): Promise<Cart> => {
    const res = await api.delete(`/cart/items/${productId}`);
    return res.data;
  },

  clearCart: async (_userId: string): Promise<void> => {
    await api.delete(`/cart`);
  },
};