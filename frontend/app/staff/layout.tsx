"use client";

import { RequireRole } from "@/components/require-role";
import { ROLE_STAFF } from "@/lib/auth";

export default function StaffLayout({ children }: { children: React.ReactNode }) {
  return <RequireRole allowedRoles={[ROLE_STAFF]}>{children}</RequireRole>;
}
