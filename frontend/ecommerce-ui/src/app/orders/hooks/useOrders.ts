import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useSelector } from "react-redux";
import toast from "react-hot-toast";
import { orderService } from "../services/orderService";
import type { RootState } from "../../core/store/store";

export const useOrders = () => {
  const qc     = useQueryClient();
  const user   = useSelector((s: RootState) => s.auth.user);
  const userId = user?.id.toString() ?? "";

  const orders = useQuery({
    queryKey: ["orders", userId],
    queryFn:  () => orderService.getUserOrders(userId),
    enabled:  !!userId,
  });

  const placeOrder = useMutation({
    mutationFn: (data: { user_email: string; user_phone: string }) =>
      orderService.placeOrder(userId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["orders", userId] });
      toast.success("Order placed successfully!");
    },
  });

  const cancelOrder = useMutation({
    mutationFn: (orderId: number) => orderService.cancelOrder(orderId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["orders", userId] });
      toast.success("Order cancelled");
    },
  });

  return {
    orders:       orders.data?.results ?? [],
    total:        orders.data?.total ?? 0,
    isLoading:    orders.isLoading,
    placeOrder:   placeOrder.mutateAsync,
    cancelOrder:  cancelOrder.mutate,
    isPlacing:    placeOrder.isPending,
  };
};