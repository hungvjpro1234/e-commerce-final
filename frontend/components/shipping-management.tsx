"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { getStatusBadgeVariant } from "@/lib/admin";
import { Shipment } from "@/types";

const SHIPPING_STATUSES = ["Processing", "Shipping", "Delivered"] as const;

export function ShippingManagement({
  queryKeyPrefix,
  title,
}: {
  queryKeyPrefix: string;
  title: string;
}) {
  const queryClient = useQueryClient();
  const [orderIdFilter, setOrderIdFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [savingOrderId, setSavingOrderId] = useState<number | null>(null);
  const [draftStatuses, setDraftStatuses] = useState<Record<number, string>>({});

  const { data: shipments, isLoading, isError } = useQuery<Shipment[]>({
    queryKey: [queryKeyPrefix, orderIdFilter, statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (orderIdFilter.trim()) params.set("order_id", orderIdFilter.trim());
      const res = await api.get(`/shipping/status${params.toString() ? `?${params.toString()}` : ""}`);
      const data = Array.isArray(res.data) ? res.data : [];
      return statusFilter ? data.filter((item: Shipment) => item.status === statusFilter) : data;
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ orderId, status }: { orderId: number; status: string }) => {
      setSavingOrderId(orderId);
      const res = await api.patch(`/shipping/status/${orderId}`, { status });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [queryKeyPrefix] });
    },
    onSettled: () => setSavingOrderId(null),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <Input
            value={orderIdFilter}
            onChange={(event) => setOrderIdFilter(event.target.value)}
            placeholder="Filter by order id"
          />
          <select
            className="flex h-9 w-full rounded-md border border-border bg-transparent px-3 py-1 text-sm shadow-sm"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            <option value="">All statuses</option>
            {SHIPPING_STATUSES.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        {isLoading && <div className="text-sm text-muted-foreground">Loading shipments...</div>}
        {isError && <div className="text-sm text-destructive">Failed to load shipments.</div>}
        {!isLoading && !isError && (!shipments || shipments.length === 0) && (
          <div className="rounded-md border border-dashed p-6 text-sm text-muted-foreground">No shipments found.</div>
        )}

        <div className="space-y-4">
          {(shipments || []).map((shipment) => {
            const draftStatus = draftStatuses[shipment.order_id] || shipment.status;
            return (
              <div key={shipment.id} className="rounded-lg border p-4">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="font-semibold">Shipment for Order #{shipment.order_id}</span>
                      <Badge variant={getStatusBadgeVariant(shipment.status)}>{shipment.status}</Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">User #{shipment.user_id}</div>
                    <div className="text-sm text-muted-foreground">{shipment.address}</div>
                  </div>
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                    <select
                      className="flex h-9 rounded-md border border-border bg-transparent px-3 py-1 text-sm shadow-sm"
                      value={draftStatus}
                      onChange={(event) =>
                        setDraftStatuses((current) => ({ ...current, [shipment.order_id]: event.target.value }))
                      }
                    >
                      {SHIPPING_STATUSES.map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                    <Button
                      onClick={() => updateMutation.mutate({ orderId: shipment.order_id, status: draftStatus })}
                      disabled={savingOrderId === shipment.order_id || draftStatus === shipment.status}
                    >
                      {savingOrderId === shipment.order_id ? "Saving..." : "Update Status"}
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
