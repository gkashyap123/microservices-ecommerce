import api from "../../core/api/axiosInstance";
import type { Order, OrderListResponse } from "../../shared/types";

export const orderService = {
  placeOrder: async (
    userId: string,
    data: { user_email: string; user_phone: string }
  ): Promise<Order> => {
    const res = await api.post(`/orders/${userId}`, data);
    return res.data;
  },

  getUserOrders: async (userId: string, page = 1): Promise<OrderListResponse> => {
    const res = await api.get(`/orders/user/${userId}`, { params: { page } });
    return res.data;
  },

  getById: async (orderId: number): Promise<Order> => {
    const res = await api.get(`/orders/${orderId}`);
    return res.data;
  },

  cancelOrder: async (orderId: number): Promise<Order> => {
    const res = await api.patch(`/orders/${orderId}/cancel`);
    return res.data;
  },
};