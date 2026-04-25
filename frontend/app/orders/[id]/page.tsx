"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import axios from "axios";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Package, Truck, CreditCard } from "lucide-react";
import { Order } from "../page";

interface PaymentStatus {
  id: number;
  order_id: number;
  amount: number;
  status: string;
}

interface ShippingStatus {
  id: number;
  order_id: number;
  address: string;
  status: string;
}

function formatMoney(value: unknown) {
  const numericValue = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numericValue) ? numericValue.toFixed(2) : "0.00";
}

function formatApiError(error: unknown) {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const detail = (error.response?.data as { detail?: string } | undefined)?.detail;
    const suffix = status ? ` (HTTP ${status})` : "";
    return `${detail || error.message || "Request failed"}${suffix}`;
  }
  if (error instanceof Error) return error.message;
  return "Unknown error";
}

export default function OrderTrackingPage() {
  const { user } = useAuthStore();
  const params = useParams();
  const orderId = params?.id != null ? String(params.id) : "";

  const { data: order, isLoading: loadingOrder } = useQuery<Order>({
    queryKey: ["order", orderId],
    queryFn: async () => {
      const res = await api.get(`/orders/${orderId}`);
      return res.data;
    },
    enabled: !!user && !!orderId,
  });

  const {
    data: payment,
    isPending: paymentLoading,
    isError: paymentError,
    error: paymentErr,
  } = useQuery<PaymentStatus>({
    queryKey: ["payment", orderId],
    queryFn: async () => {
      const res = await api.get(`/payment/status/${orderId}`);
      return res.data;
    },
    enabled: !!order && !!orderId,
  });

  const {
    data: shipping,
    isPending: shippingLoading,
    isError: shippingError,
    error: shippingErr,
  } = useQuery<ShippingStatus>({
    queryKey: ["shipping", orderId],
    queryFn: async () => {
      const res = await api.get(`/shipping/status/${orderId}`);
      return res.data;
    },
    enabled: !!order && !!orderId && order.status !== "Cancelled",
  });

  if (!user) return null;

  if (loadingOrder) {
    return <div className="max-w-3xl mx-auto space-y-6 animate-pulse p-4"><div className="h-40 bg-muted rounded-xl"></div></div>;
  }

  if (!order) {
    return <div className="text-center mt-12 text-destructive">Order not found</div>;
  }

  // Determine badge variants
  const getBadgeVariant = (status: string) => {
    if (!status) return "default";
    if (["Paid", "Success", "Completed", "Delivered"].includes(status)) return "success";
    if (["Failed", "Cancelled"].includes(status)) return "destructive";
    if (["Pending", "Processing"].includes(status)) return "warning";
    return "default";
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 p-4 md:p-0">
      <Link href="/orders" className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-foreground">
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Orders
      </Link>

      <div className="flex items-center justify-between border-b pb-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Order #{order.id}</h1>
          <p className="text-muted-foreground text-sm mt-1">Check the current status of your order.</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-muted-foreground">Total Amount</div>
          <div className="text-2xl font-bold">${formatMoney(order.total_price)}</div>
        </div>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-semibold">Order items</CardTitle>
        </CardHeader>
        <CardContent>
          {order.items && order.items.length > 0 ? (
            <ul className="divide-y rounded-md border">
              {order.items.map((line) => (
                <li key={line.id} className="flex items-center justify-between gap-4 px-3 py-2 text-sm">
                  <span className="font-medium">Product #{line.product_id}</span>
                  <span className="text-muted-foreground">Qty {line.quantity}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground">No line items returned for this order.</p>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Order Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2 text-muted-foreground">
              <Package className="w-4 h-4" />
              General Order Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold mb-1">{order.status}</div>
            <Badge variant={getBadgeVariant(order.status)}>{order.status}</Badge>
          </CardContent>
        </Card>

        {/* Payment Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2 text-muted-foreground">
              <CreditCard className="w-4 h-4" />
              Payment Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            {paymentError ? (
              <p className="text-sm text-destructive">{formatApiError(paymentErr)}</p>
            ) : payment ? (
              <>
                <div className="text-lg font-bold mb-1">{payment.status}</div>
                <Badge variant={getBadgeVariant(payment.status)}>{payment.status}</Badge>
                <div className="text-xs text-muted-foreground mt-2">Amount: ${formatMoney(payment.amount)}</div>
              </>
            ) : paymentLoading ? (
              <div className="text-sm text-muted-foreground">Loading payment...</div>
            ) : (
              <div className="text-sm text-muted-foreground">No payment record for this order.</div>
            )}
          </CardContent>
        </Card>

        {/* Shipping Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2 text-muted-foreground">
              <Truck className="w-4 h-4" />
              Shipping Pipeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            {shippingError ? (
              <p className="text-sm text-destructive">{formatApiError(shippingErr)}</p>
            ) : shipping ? (
              <>
                 <div className="text-lg font-bold mb-1">{shipping.status}</div>
                 <Badge variant={getBadgeVariant(shipping.status)}>{shipping.status}</Badge>
                 <div className="text-xs text-muted-foreground mt-2 truncate max-w-full" title={shipping.address}>
                    {shipping.address}
                 </div>
              </>
            ) : order.status === "Cancelled" ? (
              <div className="text-sm text-muted-foreground">Not applicable</div>
            ) : shippingLoading ? (
              <div className="text-sm text-muted-foreground">Loading shipping...</div>
            ) : (
               <div className="text-sm text-muted-foreground">No shipment record for this order.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
