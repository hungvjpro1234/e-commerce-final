"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Package, ArrowRight } from "lucide-react";

export interface OrderItem {
  id: number;
  product_id: number;
  quantity: number;
}

export interface Order {
  id: number;
  user_id: number;
  total_price: number;
  status: string;
  items?: OrderItem[];
}

function formatMoney(value: unknown) {
  const numericValue = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numericValue) ? numericValue.toFixed(2) : "0.00";
}

export default function OrdersListPage() {
  const { user } = useAuthStore();

  const { data: orders, isLoading, isError } = useQuery<Order[]>({
    queryKey: ["orders", user?.id],
    queryFn: async () => {
      if (!user) return [];
      const res = await api.get("/orders");
      const data = res.data as any;
      if (Array.isArray(data)) return data;
      if (Array.isArray(data?.results)) return data.results;
      if (data && typeof data === "object" && typeof data.id === "number") return [data];
      return [];
    },
    enabled: !!user,
  });

  if (!user) return null;

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="h-8 w-40 bg-muted animate-pulse rounded"></div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 w-full bg-muted animate-pulse rounded-xl"></div>
        ))}
      </div>
    );
  }

  if (isError) {
    return <div className="text-center mt-12 text-destructive font-semibold">Failed to fetch orders</div>;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Your Orders</h1>

      {!orders || orders.length === 0 ? (
        <Card className="text-center py-20 bg-muted/30">
          <CardContent className="space-y-4">
            <Package className="w-16 h-16 mx-auto text-muted-foreground opacity-50" />
            <h2 className="text-xl font-semibold">No orders found</h2>
            <p className="text-muted-foreground">You haven&apos;t placed any orders yet.</p>
            <Link href="/" className="inline-block pt-4">
              <span className="text-primary hover:underline font-medium">Continue Shopping</span>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {orders.map((order) => {
            let variant: any = "secondary";
            if (order.status === "Paid" || order.status === "Completed" || order.status === "Delivered") variant = "success";
            if (order.status === "Pending") variant = "warning";
            if (order.status === "Cancelled" || order.status === "Failed") variant = "destructive";
            if (order.status === "Shipping") variant = "default";

            return (
              <Link key={order.id} href={`/orders/${order.id}`}>
                <Card className="hover:border-primary/50 transition-colors cursor-pointer group">
                  <CardContent className="p-6 flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-bold text-lg">Order #{order.id}</span>
                        <Badge variant={variant}>{order.status}</Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Total: <span className="font-semibold text-foreground">${formatMoney(order.total_price)}</span>
                      </div>
                    </div>
                    <div>
                      <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors text-right" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
