import { useNavigate } from "react-router-dom";
import { useCart } from "../hooks/useCart";
import CartItem from "../components/CartItem";
import CartSummary from "../components/CartSummary";
import Spinner from "../../shared/components/Spinner";
import Button from "../../shared/components/Button";

export default function CartPage() {
  const navigate          = useNavigate();
  const { cart, isLoading, removeItem, updateItem } = useCart();

  if (isLoading) return (
    <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  );

  if (!cart?.items.length) return (
    <div className="max-w-2xl mx-auto px-4 py-20 text-center">
      <p className="text-gray-500 text-lg mb-4">Your cart is empty</p>
      <Button onClick={() => navigate("/products")}>Browse Products</Button>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Shopping Cart</h1>

      <div className="flex gap-8">
        {/* Items */}
        <div className="flex-1 flex flex-col gap-4">
          {cart.items.map((item) => (
            <CartItem
              key={item.product_id}
              item={item}
              onRemove={() => removeItem(item.product_id)}
              onUpdateQty={(qty) =>
                updateItem({ productId: item.product_id, quantity: qty })
              }
            />
          ))}
        </div>

        {/* Summary */}
        <aside className="w-80 shrink-0">
          <CartSummary cart={cart} onCheckout={() => navigate("/orders/place")} />
        </aside>
      </div>
    </div>
  );
}