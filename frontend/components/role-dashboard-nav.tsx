"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export interface DashboardNavItem {
  href: string;
  label: string;
  description: string;
}

export function RoleDashboardNav({
  title,
  items,
}: {
  title: string;
  items: DashboardNavItem[];
}) {
  const pathname = usePathname();

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="mb-4">
          <h2 className="text-xl font-semibold">{title}</h2>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {items.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "rounded-lg border p-4 transition-colors hover:border-primary/50 hover:bg-muted/30",
                  isActive && "border-primary bg-primary/5"
                )}
              >
                <div className="font-medium">{item.label}</div>
                <div className="mt-1 text-sm text-muted-foreground">{item.description}</div>
              </Link>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
