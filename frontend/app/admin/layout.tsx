"use client";

import { RequireRole } from "@/components/require-role";
import { ROLE_ADMIN } from "@/lib/auth";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return <RequireRole allowedRoles={[ROLE_ADMIN]}>{children}</RequireRole>;
}
