import api from "../../core/api/axiosInstance";
import type { Cart } from "../../shared/types";

export const cartService = {
  getCart: async (): Promise<Cart> => {
    // Gateway identifies user from the Authorization header; do not include user id in the path
    const res = await api.get(`/cart`);
    return res.data;
  },

  addItem: async (
    item: { product_id: number; name: string; price: number; quantity: number }
  ): Promise<Cart> => {
    const res = await api.post(`/cart/items`, item);
    return res.data;
  },

  updateItem: async (
    productId: number,
    quantity: number
  ): Promise<Cart> => {
    const res = await api.put(`/cart/items/${productId}`, { quantity });
    return res.data;
  },

  removeItem: async (productId: number): Promise<Cart> => {
    const res = await api.delete(`/cart/items/${productId}`);
    return res.data;
  },

  clearCart: async (): Promise<void> => {
    await api.delete(`/cart`);
  },
};
