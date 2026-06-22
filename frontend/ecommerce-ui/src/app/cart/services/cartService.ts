import api from "../../core/api/axiosInstance";
import type { Cart } from "../../shared/types";

export const cartService = {
  getCart: async (userId: string): Promise<Cart> => {
    const res = await api.get(`/cart/${userId}`);
    return res.data;
  },

  addItem: async (
    userId: string,
    item: { product_id: number; name: string; price: number; quantity: number }
  ): Promise<Cart> => {
    const res = await api.post(`/cart/${userId}/items`, item);
    return res.data;
  },

  updateItem: async (
    userId: string,
    productId: number,
    quantity: number
  ): Promise<Cart> => {
    const res = await api.put(`/cart/${userId}/items/${productId}`, { quantity });
    return res.data;
  },

  removeItem: async (userId: string, productId: number): Promise<Cart> => {
    const res = await api.delete(`/cart/${userId}/items/${productId}`);
    return res.data;
  },

  clearCart: async (userId: string): Promise<void> => {
    await api.delete(`/cart/${userId}`);
  },
};