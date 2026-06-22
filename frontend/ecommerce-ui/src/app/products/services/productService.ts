import api from "../../core/api/axiosInstance";
import type { Product, ProductListResponse, ProductFilters } from "../../shared/types";

export const productService = {
  getAll: async (filters: ProductFilters = {}): Promise<ProductListResponse> => {
    const res = await api.get("/products/", { params: filters });
    return res.data;
  },

  getById: async (id: number): Promise<Product> => {
    const res = await api.get(`/products/${id}`);
    return res.data;
  },
};