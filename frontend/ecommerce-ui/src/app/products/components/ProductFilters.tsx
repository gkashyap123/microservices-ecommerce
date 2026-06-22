import Input from "../../shared/components/Input";
import type { ProductFilters } from "../../shared/types";

interface Props {
  filters: ProductFilters;
  onChange: (f: ProductFilters) => void;
}

export default function ProductFilters({ filters, onChange }: Props) {
  const update = (key: keyof ProductFilters, value: string | number) =>
    onChange({ ...filters, [key]: value || undefined, page: 1 });

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4
      flex flex-col gap-4">
      <h3 className="font-semibold text-gray-900">Filters</h3>

      <Input
        label="Search"
        placeholder="Nike, shirt..."
        defaultValue={filters.search ?? ""}
        onChange={(e) => update("search", e.target.value)}
      />

      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium text-gray-700">Price Range</label>
        <div className="flex gap-2">
          <Input
            placeholder="Min"
            type="number"
            defaultValue={filters.min_price ?? ""}
            onChange={(e) => update("min_price", Number(e.target.value))}
          />
          <Input
            placeholder="Max"
            type="number"
            defaultValue={filters.max_price ?? ""}
            onChange={(e) => update("max_price", Number(e.target.value))}
          />
        </div>
      </div>
    </div>
  );
}