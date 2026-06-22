import api from "../../core/api/axiosInstance";
import type { CreatePaymentResponse, Payment } from "../../shared/types";

export const paymentService = {
  createPayment: async (data: {
    order_id: number;
    user_id: string;
    amount: number;
    user_email: string;
    user_phone: string;
  }): Promise<CreatePaymentResponse> => {
    const res = await api.post("/payments/create", data);
    return res.data;
  },

  verifyPayment: async (data: {
    razorpay_order_id: string;
    razorpay_payment_id: string;
    razorpay_signature: string;
  }): Promise<Payment> => {
    const res = await api.post("/payments/verify", data);
    return res.data;
  },

  getUserPayments: async (userId: string): Promise<Payment[]> => {
    const res = await api.get(`/payments/user/${userId}`);
    return res.data.results;
  },
};