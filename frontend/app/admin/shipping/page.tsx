"use client";

import { ManagementShell } from "@/components/management-shell";
import { ShippingManagement } from "@/components/shipping-management";

const adminNav = [
  { href: "/admin", label: "Overview", description: "Admin landing page and quick links." },
  { href: "/admin/products", label: "Products", description: "Manage catalog products and detail payloads." },
  { href: "/admin/categories", label: "Categories", description: "Manage catalog categories." },
  { href: "/admin/users", label: "Users", description: "Manage user accounts and roles." },
  { href: "/admin/orders", label: "Orders", description: "Review and update order statuses." },
  { href: "/admin/shipping", label: "Shipping", description: "Review and update shipment statuses." },
];

export default function AdminShippingPage() {
  return (
    <ManagementShell
      title="Admin Shipping Operations"
      description="Admin can manage shipping progress alongside broader operational controls."
      navTitle="Admin Navigation"
      navItems={adminNav}
    >
      <ShippingManagement queryKeyPrefix="admin-shipping" title="All Shipments" />
    </ManagementShell>
  );
}
