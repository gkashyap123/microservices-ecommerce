import { useMutation } from "@tanstack/react-query";
import { useSelector } from "react-redux";
import toast from "react-hot-toast";
import { paymentService } from "../services/paymentService";
import type { RootState } from "../../core/store/store";

export const usePayment = () => {
  const user = useSelector((s: RootState) => s.auth.user);

  const initiate = useMutation({
    mutationFn: (data: {
      order_id: number;
      amount: number;
      user_email: string;
      user_phone: string;
    }) =>
      paymentService.createPayment({
        ...data,
        user_id: user!.id.toString(),
      }),
  });

  const verify = useMutation({
    mutationFn: paymentService.verifyPayment,
    onSuccess: () => toast.success("Payment successful! 🎉"),
    onError:   () => toast.error("Payment verification failed"),
  });

  return {
    initiatePayment: initiate.mutateAsync,
    verifyPayment:   verify.mutateAsync,
    isInitiating:    initiate.isPending,
    isVerifying:     verify.isPending,
  };
};