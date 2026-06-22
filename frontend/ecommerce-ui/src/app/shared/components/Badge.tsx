const colors: Record<string, string> = {
  PENDING:        "bg-yellow-100 text-yellow-800",
  CONFIRMED:      "bg-blue-100 text-blue-800",
  SHIPPED:        "bg-purple-100 text-purple-800",
  DELIVERED:      "bg-green-100 text-green-800",
  CANCELLED:      "bg-gray-100 text-gray-800",
  FAILED:         "bg-red-100 text-red-800",
  SUCCESS:        "bg-green-100 text-green-800",
  CREATED:        "bg-yellow-100 text-yellow-800",
  REFUNDED:       "bg-orange-100 text-orange-800",
  PARTIAL_REFUND: "bg-orange-100 text-orange-800",
};

export default function Badge({ label }: { label: string }) {
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium
      ${colors[label] ?? "bg-gray-100 text-gray-700"}`}>
      {label}
    </span>
  );
}