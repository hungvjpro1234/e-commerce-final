"use client";

import { RoleDashboardNav, type DashboardNavItem } from "@/components/role-dashboard-nav";

export function ManagementShell({
  title,
  description,
  navTitle,
  navItems,
  children,
}: {
  title: string;
  description: string;
  navTitle: string;
  navItems: DashboardNavItem[];
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
        <p className="mt-1 text-muted-foreground">{description}</p>
      </div>
      <RoleDashboardNav title={navTitle} items={navItems} />
      {children}
    </div>
  );
}
