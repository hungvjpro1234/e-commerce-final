"use client";

import { ManagementShell } from "@/components/management-shell";
import { ShippingManagement } from "@/components/shipping-management";

const staffNav = [
  { href: "/staff", label: "Overview", description: "Landing page for staff operations." },
  { href: "/staff/orders", label: "Orders", description: "Review and update order statuses." },
  { href: "/staff/shipping", label: "Shipping", description: "Review and update shipment statuses." },
];

export default function StaffShippingPage() {
  return (
    <ManagementShell
      title="Staff Shipping Operations"
      description="Handle shipment progress and fulfillment updates."
      navTitle="Staff Navigation"
      navItems={staffNav}
    >
      <ShippingManagement queryKeyPrefix="staff-shipping" title="All Shipments" />
    </ManagementShell>
  );
}
