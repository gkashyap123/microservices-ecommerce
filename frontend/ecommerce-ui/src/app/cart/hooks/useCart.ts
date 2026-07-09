import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { cartService } from "../services/cartService";
import { setCart, clearCart } from "../../core/store/slices/cartSlice";
import type { RootState } from "../../core/store/store";

export const useCart = () => {
  const dispatch     = useDispatch();
  const qc           = useQueryClient();
  const navigate     = useNavigate();
  const userId       = useSelector((s: RootState) => s.auth.user?.id.toString());

  const requireLogin = () => {
    if (!userId) {
      toast.error("Please login to add items to your cart.");
      navigate("/login");
      throw new Error("User is not authenticated.");
    }
    return userId;
  };

  const { data: cart, isLoading } = useQuery({
    queryKey: ["cart", userId],
    queryFn:  async () => {
      const c = await cartService.getCart(requireLogin());
      dispatch(setCart(c));
      return c;
    },
    enabled: !!userId,
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ["cart", userId] });

  const addItem = useMutation({
    mutationFn: (item: {
      product_id: number; name: string; price: number; quantity: number;
    }) => cartService.addItem(requireLogin(), item),
    onSuccess: (c) => { dispatch(setCart(c)); invalidate(); toast.success("Added to cart"); },
  });

  const updateItem = useMutation({
    mutationFn: ({ productId, quantity }: { productId: number; quantity: number }) =>
      cartService.updateItem(requireLogin(), productId, quantity),
    onSuccess: (c) => { dispatch(setCart(c)); invalidate(); },
  });

  const removeItem = useMutation({
    mutationFn: (productId: number) => cartService.removeItem(requireLogin(), productId),
    onSuccess: (c) => { dispatch(setCart(c)); invalidate(); toast.success("Item removed"); },
  });

  const clear = useMutation({
    mutationFn: () => cartService.clearCart(requireLogin()),
    onSuccess: () => { dispatch(clearCart()); invalidate(); },
  });

  return {
    cart,
    isLoading,
    addItem:    addItem.mutate,
    updateItem: updateItem.mutate,
    removeItem: removeItem.mutate,
    clearCart:  clear.mutate,
    isAdding:   addItem.isPending,
  };
};