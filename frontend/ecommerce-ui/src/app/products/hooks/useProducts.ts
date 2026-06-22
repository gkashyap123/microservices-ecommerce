import { useQuery } from "@tanstack/react-query";
import { productService } from "../services/productService";
import type { ProductFilters } from "../../shared/types";

export const useProducts = (filters: ProductFilters = {}) =>
  useQuery({
    queryKey: ["products", filters],
    queryFn:  () => productService.getAll(filters),
  });

export const useProduct = (id: number) =>
  useQuery({
    queryKey: ["product", id],
    queryFn:  () => productService.getById(id),
    enabled:  !!id,
  });