import { Trash2 } from "lucide-react";
import type { CartItem as CartItemType } from "../../shared/types";

interface Props {
  item: CartItemType;
  onRemove: () => void;
  onUpdateQty: (qty: number) => void;
}

export default function CartItem({ item, onRemove, onUpdateQty }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4
      flex items-center gap-4">
      <div className="flex-1">
        <p className="font-medium text-gray-900">{item.name}</p>
        <p className="text-sm text-gray-500">₹{item.price.toLocaleString()}</p>
      </div>

      {/* Quantity stepper */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => item.quantity > 1 && onUpdateQty(item.quantity - 1)}
          className="w-8 h-8 rounded-lg border border-gray-300
            flex items-center justify-center hover:bg-gray-50 text-lg"
        >−</button>
        <span className="w-8 text-center font-medium">{item.quantity}</span>
        <button
          onClick={() => onUpdateQty(item.quantity + 1)}
          className="w-8 h-8 rounded-lg border border-gray-300
            flex items-center justify-center hover:bg-gray-50 text-lg"
        >+</button>
      </div>

      <p className="w-24 text-right font-semibold text-gray-900">
        ₹{item.subtotal.toLocaleString()}
      </p>

      <button onClick={onRemove}
        className="text-red-400 hover:text-red-600 transition-colors">
        <Trash2 size={18} />
      </button>
    </div>
  );
}