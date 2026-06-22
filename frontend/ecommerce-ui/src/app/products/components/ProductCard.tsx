import { Link } from "react-router-dom";
import { ShoppingCart } from "lucide-react";
import Button from "../../shared/components/Button";
import type { Product } from "../../shared/types";

interface Props {
  product: Product;
  onAddToCart: () => void;
  isAdding: boolean;
}

export default function ProductCard({ product, onAddToCart, isAdding }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200
      hover:shadow-md transition-shadow p-4 flex flex-col gap-3">

      {/* Category badge */}
      <span className="text-xs text-blue-600 font-medium">
        {product.category.name}
      </span>

      <Link to={`/products/${product.id}`}>
        <h3 className="font-semibold text-gray-900 hover:text-blue-600
          transition-colors line-clamp-2">
          {product.name}
        </h3>
      </Link>

      {product.description && (
        <p className="text-sm text-gray-500 line-clamp-2">
          {product.description}
        </p>
      )}

      <div className="flex items-center justify-between mt-auto">
        <div>
          <p className="text-lg font-bold text-gray-900">
            ₹{product.price.toLocaleString()}
          </p>
          <p className={`text-xs ${
            product.stock > 0 ? "text-green-600" : "text-red-500"
          }`}>
            {product.stock > 0 ? `${product.stock} in stock` : "Out of stock"}
          </p>
        </div>

        <Button
          onClick={onAddToCart}
          disabled={product.stock === 0}
          isLoading={isAdding}
          variant="primary"
          className="!px-3 !py-2"
        >
          <ShoppingCart size={16} />
        </Button>
      </div>
    </div>
  );
}