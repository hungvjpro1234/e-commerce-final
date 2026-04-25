"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { Cart, Product, CartItem } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Minus, Plus, Trash2, ArrowRight, ShoppingCart } from "lucide-react";
import { useState } from "react";

function formatMoney(value: unknown) {
  const numericValue = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numericValue) ? numericValue.toFixed(2) : "0.00";
}

function CartItemRow({ item }: { item: CartItem }) {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const [isUpdating, setIsUpdating] = useState(false);

  const { data: product } = useQuery<Product>({
    queryKey: ["product", item.product_id],
    queryFn: async () => {
      const res = await api.get(`/products/${item.product_id}`);
      return res.data;
    },
  });

  const updateMutation = useMutation({
    mutationFn: async (newQuantity: number) => {
      if (!user) return;
      setIsUpdating(true);
      const res = await api.put("/cart/update", {
        product_id: item.product_id,
        quantity: newQuantity,
      });
      return res.data;
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["cart", user?.id] });
      setIsUpdating(false);
    },
  });

  const removeMutation = useMutation({
    mutationFn: async () => {
      if (!user) return;
      setIsUpdating(true);
      const res = await api.delete("/cart/remove", {
        data: {
          product_id: item.product_id,
        },
      });
      return res.data;
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["cart", user?.id] });
      setIsUpdating(false);
    },
  });

  if (!product) return (
    <div className="flex items-center justify-between p-4 border-b animate-pulse">
      <div className="h-10 w-48 bg-muted rounded"></div>
    </div>
  );

  const imgSrc = `https://picsum.photos/seed/${product.id}/150/150`;
  const isOutOfStock = product.stock < item.quantity;
  const lineTotal = product.price * item.quantity;

  return (
    <div className={`flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 border-b gap-4 transition-opacity ${isUpdating ? "opacity-50 pointer-events-none" : ""}`}>
      <div className="flex items-center gap-4 flex-1">
        <Link href={`/products/${product.id}`} className="block w-16 h-16 rounded overflow-hidden border bg-muted flex-shrink-0">
           <img src={imgSrc} alt={product.name} className="w-full h-full object-cover" />
        </Link>
        <div>
          <Link href={`/products/${product.id}`} className="font-semibold hover:text-primary transition-colors text-sm sm:text-base line-clamp-1">
            {product.name}
          </Link>
          <div className="text-muted-foreground text-sm font-medium mt-1">
            ${formatMoney(product.price)}
          </div>
          {isOutOfStock && (
            <div className="text-destructive text-xs font-semibold mt-1">
              Insufficient Stock (Available: {product.stock})
            </div>
          )}
        </div>
      </div>
      
      <div className="flex items-center justify-between w-full sm:w-auto gap-8 sm:gap-12">
        <div className="flex items-center border rounded-md">
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => updateMutation.mutate(item.quantity - 1)} disabled={item.quantity <= 1}>
            <Minus className="w-3 h-3" />
          </Button>
          <span className="w-8 text-center text-sm font-medium">{item.quantity}</span>
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => updateMutation.mutate(item.quantity + 1)} disabled={item.quantity >= product.stock}>
            <Plus className="w-3 h-3" />
          </Button>
        </div>

        <div className="font-bold w-20 text-right">
          ${formatMoney(lineTotal)}
        </div>

        <Button variant="ghost" size="icon" className="text-destructive hover:bg-destructive/10" onClick={() => removeMutation.mutate()}>
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}

export default function CartPage() {
  const { user } = useAuthStore();

  const { data: cart, isLoading } = useQuery<Cart>({
    queryKey: ["cart", user?.id],
    queryFn: async () => {
      if (!user) return { id: 0, user_id: 0, items: [] };
      try {
        const res = await api.get("/cart/");
        return res.data;
      } catch (err: any) {
        if (err.response?.status === 404) return { id: 0, user_id: user.id, items: [] };
        throw err;
      }
    },
    enabled: !!user,
  });

  // Calculate generic subtotal in JS since cart endpoint just stores IDs,
  // but we must fetch all product prices correctly. 
  // For precise total, we'll let the user see the visual subtotal based on the line items.
  // The actual Subtotal depends on the dynamic queries.

  // A more robust approach fetches all products for cart items in parallel,
  // but using individual CartItemRow works for visual presentation.

  if (!user) return null;

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="h-8 w-32 bg-muted animate-pulse rounded"></div>
        <Card>
          <CardContent className="p-6">
             <div className="h-20 w-full bg-muted animate-pulse rounded mb-4"></div>
             <div className="h-20 w-full bg-muted animate-pulse rounded"></div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const items = cart?.items || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Your Cart</h1>
      
      {items.length === 0 ? (
        <Card className="text-center py-20 bg-muted/30">
          <CardContent className="space-y-4">
            <ShoppingCart className="w-16 h-16 mx-auto text-muted-foreground opacity-50" />
            <h2 className="text-xl font-semibold">Your cart is empty</h2>
            <p className="text-muted-foreground">Looks like you haven&apos;t added anything yet.</p>
            <div className="pt-4">
              <Link href="/">
                <Button>Start Shopping</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Card>
              <CardContent className="p-0">
                {items.map((item) => (
                  <CartItemRow key={`${item.product_id}`} item={item} />
                ))}
              </CardContent>
            </Card>
          </div>
          
          <div>
            <Card className="sticky top-24">
              <CardContent className="p-6 space-y-6">
                <h3 className="text-lg font-semibold border-b pb-4">Order Summary</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Items</span>
                    <span className="font-medium">{items.reduce((acc, curr) => acc + curr.quantity, 0)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Shipping</span>
                    <span className="font-medium">Calculated at checkout</span>
                  </div>
                </div>
                <div className="pt-4 border-t">
                  <Link href="/checkout" className="w-full block">
                    <Button className="w-full text-base h-12">
                      Proceed to Checkout
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
