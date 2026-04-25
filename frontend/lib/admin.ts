type BadgeVariant = "default" | "secondary" | "destructive" | "outline" | "success" | "warning";

export function formatMoney(value: unknown) {
  const numericValue = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numericValue) ? numericValue.toFixed(2) : "0.00";
}

export function getStatusBadgeVariant(status: string): BadgeVariant {
  if (["Paid", "Success", "Completed", "Delivered"].includes(status)) return "success";
  if (["Failed", "Cancelled"].includes(status)) return "destructive";
  if (["Pending", "Processing"].includes(status)) return "warning";
  if (["Shipping"].includes(status)) return "default";
  return "secondary";
}
