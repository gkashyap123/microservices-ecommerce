import { useState } from "react";
import { useProducts } from "../hooks/useProducts";
import { useCart } from "../../cart/hooks/useCart";
import ProductCard from "../components/ProductCard";
import ProductFilters from "../components/ProductFilters";
import Spinner from "../../shared/components/Spinner";
import type { ProductFilters as Filters } from "../../shared/types";

export default function ProductsPage() {
  const [filters, setFilters] = useState<Filters>({ page: 1, page_size: 12 });
  const { data, isLoading }   = useProducts(filters);
  const { addItem, isAdding } = useCart();

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Products</h1>

      <div className="flex gap-8">
        {/* Filters sidebar */}
        <aside className="w-64 shrink-0">
          <ProductFilters filters={filters} onChange={setFilters} />
        </aside>

        {/* Product grid */}
        <div className="flex-1">
          {isLoading ? (
            <div className="flex justify-center py-20">
              <Spinner size="lg" />
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-500 mb-4">
                {data?.total ?? 0} products found
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {data?.results.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onAddToCart={() =>
                      addItem({
                        product_id: product.id,
                        name: product.name,
                        price: product.price,
                        quantity: 1,
                      })
                    }
                    isAdding={isAdding}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}