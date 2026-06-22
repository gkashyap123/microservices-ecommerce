import { usePayment } from "../hooks/usePayment";
//import { useOrders } from "../../orders/hooks/useOrders";
import Button from "../../shared/components/Button";
import type { Order } from "../../shared/types";

interface Props { order: Order; userEmail: string; userPhone: string; }

export default function RazorpayCheckout({ order, userEmail, userPhone }: Props) {
  const { initiatePayment, verifyPayment, isInitiating } = usePayment();

  const handlePay = async () => {
    const paymentData = await initiatePayment({
      order_id:   order.id,
      amount:     order.total_price,
      user_email: userEmail,
      user_phone: userPhone,
    });

    const options = {
      key:      paymentData.razorpay_key_id,
      amount:   paymentData.amount * 100,
      currency: paymentData.currency,
      order_id: paymentData.razorpay_order_id,
      name:     "ShopApp",
      prefill:  { email: userEmail, contact: userPhone },
      handler:  async (response: {
        razorpay_order_id: string;
        razorpay_payment_id: string;
        razorpay_signature: string;
      }) => {
        await verifyPayment({
          razorpay_order_id:   response.razorpay_order_id,
          razorpay_payment_id: response.razorpay_payment_id,
          razorpay_signature:  response.razorpay_signature,
        });
      },
    };

    // @ts-ignore — Razorpay loaded via CDN script tag
    const rzp = new window.Razorpay(options);
    rzp.open();
  };

  return (
    <Button onClick={handlePay} isLoading={isInitiating} fullWidth>
      Pay ₹{order.total_price.toLocaleString()}
    </Button>
  );
}