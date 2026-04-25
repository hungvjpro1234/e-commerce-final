"use client";

import { RequireRole } from "@/components/require-role";
import { ROLE_CUSTOMER } from "@/lib/auth";

export default function CheckoutLayout({ children }: { children: React.ReactNode }) {
  return <RequireRole allowedRoles={[ROLE_CUSTOMER]}>{children}</RequireRole>;
}
