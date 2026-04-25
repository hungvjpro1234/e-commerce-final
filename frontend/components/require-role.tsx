"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { RequireAuth } from "@/components/require-auth";
import { getDefaultRouteForRole, hasRequiredRole, type AppRole } from "@/lib/auth";
import { useAuthStore } from "@/lib/store";

function GuardedRoleContent({
  allowedRoles,
  children,
}: {
  allowedRoles: AppRole[];
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user } = useAuthStore();

  useEffect(() => {
    if (user && !hasRequiredRole(user.role, allowedRoles)) {
      router.replace(getDefaultRouteForRole(user.role));
    }
  }, [allowedRoles, router, user]);

  if (!user || !hasRequiredRole(user.role, allowedRoles)) {
    return null;
  }

  return <>{children}</>;
}

export function RequireRole({
  allowedRoles,
  children,
}: {
  allowedRoles: AppRole[];
  children: React.ReactNode;
}) {
  return (
    <RequireAuth>
      <GuardedRoleContent allowedRoles={allowedRoles}>{children}</GuardedRoleContent>
    </RequireAuth>
  );
}
