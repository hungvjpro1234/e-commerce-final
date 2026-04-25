"use client";

import { RequireRole } from "@/components/require-role";
import { ROLE_CUSTOMER } from "@/lib/auth";

export default function OrdersLayout({ children }: { children: React.ReactNode }) {
  return <RequireRole allowedRoles={[ROLE_CUSTOMER]}>{children}</RequireRole>;
}
