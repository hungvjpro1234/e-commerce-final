"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ManagementShell } from "@/components/management-shell";

const adminNav = [
  { href: "/admin", label: "Overview", description: "Admin landing page and quick links." },
  { href: "/admin/products", label: "Products", description: "Manage catalog products and detail payloads." },
  { href: "/admin/categories", label: "Categories", description: "Manage catalog categories." },
  { href: "/admin/users", label: "Users", description: "Manage user accounts and roles." },
  { href: "/admin/orders", label: "Orders", description: "Review and update order statuses." },
  { href: "/admin/shipping", label: "Shipping", description: "Review and update shipment statuses." },
];

export default function AdminPage() {
  return (
    <ManagementShell
      title="Admin Dashboard"
      description="Operate catalog, user, order, and shipping workflows with full administrative access."
      navTitle="Admin Navigation"
      navItems={adminNav}
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {adminNav.slice(1).map((item) => (
          <Card key={item.href}>
            <CardHeader>
              <CardTitle>{item.label}</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">{item.description}</CardContent>
          </Card>
        ))}
      </div>
    </ManagementShell>
  );
}
