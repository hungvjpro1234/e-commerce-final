"use client";

import { ManagementShell } from "@/components/management-shell";
import { OrderManagement } from "@/components/order-management";

const adminNav = [
  { href: "/admin", label: "Overview", description: "Admin landing page and quick links." },
  { href: "/admin/products", label: "Products", description: "Manage catalog products and detail payloads." },
  { href: "/admin/categories", label: "Categories", description: "Manage catalog categories." },
  { href: "/admin/users", label: "Users", description: "Manage user accounts and roles." },
  { href: "/admin/orders", label: "Orders", description: "Review and update order statuses." },
  { href: "/admin/shipping", label: "Shipping", description: "Review and update shipment statuses." },
];

export default function AdminOrdersPage() {
  return (
    <ManagementShell
      title="Admin Order Operations"
      description="Admin can review and override order statuses across the system."
      navTitle="Admin Navigation"
      navItems={adminNav}
    >
      <OrderManagement queryKeyPrefix="admin-orders" title="All Orders" />
    </ManagementShell>
  );
}
