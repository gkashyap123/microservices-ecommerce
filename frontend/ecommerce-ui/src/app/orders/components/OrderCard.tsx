import { Link } from "react-router-dom";
import Badge from "../../shared/components/Badge";
import type { Order } from "../../shared/types";

export default function OrderCard({ order }: { order: Order }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="font-semibold text-gray-900">Order #{order.id}</p>
          <p className="text-sm text-gray-500">
            {new Date(order.created_at).toLocaleDateString("en-IN", {
              day: "numeric", month: "short", year: "numeric",
            })}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge label={order.status} />
          <p className="font-bold text-gray-900">
            ₹{order.total_price.toLocaleString()}
          </p>
        </div>
      </div>

      <div className="text-sm text-gray-500 mb-3">
        {order.items.map((i) => i.name).join(", ")}
      </div>

      <Link
        to={`/orders/${order.id}`}
        className="text-sm text-blue-600 hover:underline"
      >
        View Details →
      </Link>
    </div>
  );
}