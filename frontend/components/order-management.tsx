"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { formatMoney, getStatusBadgeVariant } from "@/lib/admin";
import { Order } from "@/types";

const ORDER_STATUSES = ["Pending", "Paid", "Shipping", "Completed", "Cancelled"] as const;

export function OrderManagement({
  queryKeyPrefix,
  title,
}: {
  queryKeyPrefix: string;
  title: string;
}) {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState("");
  const [userIdFilter, setUserIdFilter] = useState("");
  const [savingOrderId, setSavingOrderId] = useState<number | null>(null);
  const [draftStatuses, setDraftStatuses] = useState<Record<number, string>>({});

  const { data: orders, isLoading, isError } = useQuery<Order[]>({
    queryKey: [queryKeyPrefix, userIdFilter, statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (userIdFilter.trim()) params.set("user_id", userIdFilter.trim());
      const res = await api.get(`/orders${params.toString() ? `?${params.toString()}` : ""}`);
      const data = res.data;
      const collection = Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : [];
      return statusFilter ? collection.filter((item: Order) => item.status === statusFilter) : collection;
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ orderId, status }: { orderId: number; status: string }) => {
      setSavingOrderId(orderId);
      const res = await api.patch(`/orders/${orderId}`, { status });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKeyPrefix] });
    },
    onSettled: () => setSavingOrderId(null),
  });

  const totalValue = useMemo(
    () => (orders || []).reduce((sum, order) => sum + Number(order.total_price || 0), 0),
    [orders]
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Input
              value={userIdFilter}
              onChange={(event) => setUserIdFilter(event.target.value)}
              placeholder="Filter by user id"
            />
            <select
              className="flex h-9 w-full rounded-md border border-border bg-transparent px-3 py-1 text-sm shadow-sm"
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
            >
              <option value="">All statuses</option>
              {ORDER_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
            <div className="rounded-md border px-3 py-2 text-sm text-muted-foreground">
              Total value: <span className="font-semibold text-foreground">${formatMoney(totalValue)}</span>
            </div>
          </div>

          {isLoading && <div className="text-sm text-muted-foreground">Loading orders...</div>}
          {isError && <div className="text-sm text-destructive">Failed to load orders.</div>}
          {!isLoading && !isError && (!orders || orders.length === 0) && (
            <div className="rounded-md border border-dashed p-6 text-sm text-muted-foreground">No orders found.</div>
          )}

          <div className="space-y-4">
            {(orders || []).map((order) => {
              const draftStatus = draftStatuses[order.id] || order.status;
              return (
                <div key={order.id} className="rounded-lg border p-4">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                        <span className="font-semibold">Order #{order.id}</span>
                        <Badge variant={getStatusBadgeVariant(order.status)}>{order.status}</Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        User #{order.user_id} · ${formatMoney(order.total_price)} · {order.items.length} item(s)
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Items: {order.items.map((item) => `P${item.product_id} × ${item.quantity}`).join(", ")}
                      </div>
                    </div>
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                      <select
                        className="flex h-9 rounded-md border border-border bg-transparent px-3 py-1 text-sm shadow-sm"
                        value={draftStatus}
                        onChange={(event) =>
                          setDraftStatuses((current) => ({ ...current, [order.id]: event.target.value }))
                        }
                      >
                        {ORDER_STATUSES.map((status) => (
                          <option key={status} value={status}>
                            {status}
                          </option>
                        ))}
                      </select>
                      <Button
                        onClick={() => updateMutation.mutate({ orderId: order.id, status: draftStatus })}
                        disabled={savingOrderId === order.id || draftStatus === order.status}
                      >
                        {savingOrderId === order.id ? "Saving..." : "Update Status"}
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
