"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && !user) {
      router.replace(`/login?next=${encodeURIComponent(pathname || "/")}`);
    }
  }, [mounted, pathname, router, user]);

  if (!mounted || !user) {
    return null;
  }

  return <>{children}</>;
}
