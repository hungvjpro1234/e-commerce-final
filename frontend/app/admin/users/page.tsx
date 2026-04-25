"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { ManagementShell } from "@/components/management-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { UserFormValues, UserRecord } from "@/types";

const adminNav = [
  { href: "/admin", label: "Overview", description: "Admin landing page and quick links." },
  { href: "/admin/products", label: "Products", description: "Manage catalog products and detail payloads." },
  { href: "/admin/categories", label: "Categories", description: "Manage catalog categories." },
  { href: "/admin/users", label: "Users", description: "Manage user accounts and roles." },
  { href: "/admin/orders", label: "Orders", description: "Review and update order statuses." },
  { href: "/admin/shipping", label: "Shipping", description: "Review and update shipment statuses." },
];

const defaultForm: UserFormValues = {
  username: "",
  email: "",
  password: "",
  role: "customer",
  first_name: "",
  last_name: "",
};

export default function AdminUsersPage() {
  const queryClient = useQueryClient();
  const [editingUser, setEditingUser] = useState<UserRecord | null>(null);
  const [form, setForm] = useState<UserFormValues>(defaultForm);

  const { data: users } = useQuery<UserRecord[]>({
    queryKey: ["admin-users"],
    queryFn: async () => (await api.get("/users")).data,
  });

  const saveMutation = useMutation({
    mutationFn: async (payload: UserFormValues) => {
      const requestBody = editingUser
        ? {
            username: payload.username,
            email: payload.email,
            role: payload.role,
            first_name: payload.first_name,
            last_name: payload.last_name,
            ...(payload.password ? { password: payload.password } : {}),
          }
        : payload;

      if (editingUser) {
        return (await api.patch(`/users/${editingUser.id}`, requestBody)).data;
      }
      return (await api.post("/users", requestBody)).data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      setEditingUser(null);
      setForm(defaultForm);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (userId: number) => api.delete(`/users/${userId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-users"] }),
  });

  return (
    <ManagementShell
      title="Admin User Management"
      description="Create, update, and delete users while controlling their application roles."
      navTitle="Admin Navigation"
      navItems={adminNav}
    >
      <div className="grid gap-6 xl:grid-cols-[420px_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <CardTitle>{editingUser ? `Edit User #${editingUser.id}` : "Create User"}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="Username" />
            <Input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email" />
            <Input
              type="password"
              value={form.password || ""}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder={editingUser ? "Leave blank to keep password" : "Password"}
            />
            <select
              className="flex h-9 w-full rounded-md border border-border bg-transparent px-3 py-1 text-sm shadow-sm"
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value as UserFormValues["role"] })}
            >
              <option value="customer">Customer</option>
              <option value="staff">Staff</option>
              <option value="admin">Admin</option>
            </select>
            <div className="grid gap-4 md:grid-cols-2">
              <Input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} placeholder="First name" />
              <Input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} placeholder="Last name" />
            </div>
            <div className="flex gap-2">
              <Button
                onClick={() => saveMutation.mutate(form)}
                disabled={!form.username || !form.email || (!editingUser && !form.password) || saveMutation.isPending}
              >
                {saveMutation.isPending ? "Saving..." : editingUser ? "Update User" : "Create User"}
              </Button>
              {editingUser && (
                <Button variant="outline" onClick={() => { setEditingUser(null); setForm(defaultForm); }}>
                  Cancel
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Users</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {(users || []).map((user) => (
              <div key={user.id} className="rounded-lg border p-4">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="font-semibold">{user.username}</span>
                      <Badge variant="secondary">{user.role}</Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {user.email} · {user.first_name || "-"} {user.last_name || ""}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setEditingUser(user);
                        setForm({
                          username: user.username,
                          email: user.email,
                          password: "",
                          role: user.role as UserFormValues["role"],
                          first_name: user.first_name,
                          last_name: user.last_name,
                        });
                      }}
                    >
                      Edit
                    </Button>
                    <Button variant="destructive" onClick={() => deleteMutation.mutate(user.id)}>
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </ManagementShell>
  );
}
