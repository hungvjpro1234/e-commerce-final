"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { ManagementShell } from "@/components/management-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Category } from "@/types";

const adminNav = [
  { href: "/admin", label: "Overview", description: "Admin landing page and quick links." },
  { href: "/admin/products", label: "Products", description: "Manage catalog products and detail payloads." },
  { href: "/admin/categories", label: "Categories", description: "Manage catalog categories." },
  { href: "/admin/users", label: "Users", description: "Manage user accounts and roles." },
  { href: "/admin/orders", label: "Orders", description: "Review and update order statuses." },
  { href: "/admin/shipping", label: "Shipping", description: "Review and update shipment statuses." },
];

export default function AdminCategoriesPage() {
  const queryClient = useQueryClient();
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [name, setName] = useState("");

  const { data: categories } = useQuery<Category[]>({
    queryKey: ["admin-categories"],
    queryFn: async () => (await api.get("/categories")).data,
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (editingCategory) {
        return (await api.patch(`/categories/${editingCategory.id}`, { name })).data;
      }
      return (await api.post("/categories", { name })).data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-categories"] });
      setEditingCategory(null);
      setName("");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (categoryId: number) => api.delete(`/categories/${categoryId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-categories"] }),
  });

  return (
    <ManagementShell
      title="Admin Category Management"
      description="Create, update, and delete product categories."
      navTitle="Admin Navigation"
      navItems={adminNav}
    >
      <div className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <CardTitle>{editingCategory ? `Edit Category #${editingCategory.id}` : "Create Category"}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Category name" />
            <div className="flex gap-2">
              <Button onClick={() => saveMutation.mutate()} disabled={!name.trim() || saveMutation.isPending}>
                {saveMutation.isPending ? "Saving..." : editingCategory ? "Update Category" : "Create Category"}
              </Button>
              {editingCategory && (
                <Button variant="outline" onClick={() => { setEditingCategory(null); setName(""); }}>
                  Cancel
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Categories</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {(categories || []).map((category) => (
              <div key={category.id} className="flex items-center justify-between rounded-lg border p-4">
                <div className="font-medium">{category.name}</div>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => { setEditingCategory(category); setName(category.name); }}>
                    Edit
                  </Button>
                  <Button variant="destructive" onClick={() => deleteMutation.mutate(category.id)}>
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </ManagementShell>
  );
}
