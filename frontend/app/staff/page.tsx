"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ManagementShell } from "@/components/management-shell";

const staffNav = [
  { href: "/staff", label: "Overview", description: "Landing page for staff operations." },
  { href: "/staff/orders", label: "Orders", description: "Review and update order statuses." },
  { href: "/staff/shipping", label: "Shipping", description: "Review and update shipment statuses." },
];

export default function StaffPage() {
  return (
    <ManagementShell
      title="Staff Dashboard"
      description="Operate order and shipping workflows with role-restricted access."
      navTitle="Staff Navigation"
      navItems={staffNav}
    >
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Order Handling</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Review all orders, filter by user or status, and move them through the allowed status pipeline.
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Shipping Handling</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Track fulfillment and update shipping progress without exposing catalog or user management actions.
          </CardContent>
        </Card>
      </div>
    </ManagementShell>
  );
}
