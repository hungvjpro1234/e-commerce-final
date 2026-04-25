"use client";

import { ManagementShell } from "@/components/management-shell";
import { OrderManagement } from "@/components/order-management";

const staffNav = [
  { href: "/staff", label: "Overview", description: "Landing page for staff operations." },
  { href: "/staff/orders", label: "Orders", description: "Review and update order statuses." },
  { href: "/staff/shipping", label: "Shipping", description: "Review and update shipment statuses." },
];

export default function StaffOrdersPage() {
  return (
    <ManagementShell
      title="Staff Order Operations"
      description="Handle order status transitions across the system."
      navTitle="Staff Navigation"
      navItems={staffNav}
    >
      <OrderManagement queryKeyPrefix="staff-orders" title="All Orders" />
    </ManagementShell>
  );
}
