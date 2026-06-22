import Button from "../../shared/components/Button";
import type { Cart } from "../../shared/types";

interface Props { cart: Cart; onCheckout: () => void; }

export default function CartSummary({ cart, onCheckout }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6
      flex flex-col gap-4 sticky top-24">
      <h3 className="font-semibold text-gray-900 text-lg">Order Summary</h3>

      <div className="flex flex-col gap-2 text-sm">
        <div className="flex justify-between text-gray-600">
          <span>Items ({cart.total_items})</span>
          <span>₹{cart.total_price.toLocaleString()}</span>
        </div>
        <div className="flex justify-between text-gray-600">
          <span>Shipping</span>
          <span className="text-green-600">Free</span>
        </div>
        <div className="border-t border-gray-200 pt-2 mt-1
          flex justify-between font-bold text-gray-900 text-base">
          <span>Total</span>
          <span>₹{cart.total_price.toLocaleString()}</span>
        </div>
      </div>

      <Button onClick={onCheckout} fullWidth>
        Proceed to Checkout
      </Button>
    </div>
  );
}