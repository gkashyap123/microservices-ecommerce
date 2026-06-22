import { useOrders } from "../hooks/useOrders";
import OrderCard from "../components/OrderCard";
import Spinner from "../../shared/components/Spinner";

export default function OrdersPage() {
  const { orders, isLoading } = useOrders();

  if (isLoading) return (
    <div className="flex justify-center py-20"><Spinner size="lg" /></div>
  );

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Orders</h1>
      {orders.length === 0 ? (
        <p className="text-center text-gray-500 py-20">No orders yet</p>
      ) : (
        <div className="flex flex-col gap-4">
          {orders.map((order) => (
            <OrderCard key={order.id} order={order} />
          ))}
        </div>
      )}
    </div>
  );
}