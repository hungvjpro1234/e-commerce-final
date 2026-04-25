"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import api from "@/lib/api";
import { Product } from "@/types";
import { useAuthStore } from "@/lib/store";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Minus, Plus, ShoppingCart, ArrowLeft } from "lucide-react";
import Link from "next/link";

function formatMoney(value: unknown) {
  const numericValue = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numericValue) ? numericValue.toFixed(2) : "0.00";
}

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthStore();
  const [quantity, setQuantity] = useState(1);
  const [addMsg, setAddMsg] = useState("");

  const { data: product, isLoading, isError } = useQuery<Product>({
    queryKey: ["product", params.id],
    queryFn: async () => {
      const res = await api.get(`/products/${params.id}`);
      return res.data;
    },
  });

  const addMutation = useMutation({
    mutationFn: async () => {
      if (!user) throw new Error("Must be logged in");
      const payload = {
        product_id: product?.id,
        quantity: quantity,
      };
      const res = await api.post("/cart/add", payload);
      return res.data;
    },
    onSuccess: () => {
      setAddMsg("Added to cart successfully!");
      setTimeout(() => setAddMsg(""), 3000);
    },
    onError: () => {
      if (!user) {
        router.push("/login");
      } else {
        setAddMsg("Failed to add to cart.");
      }
    },
  });

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6 max-w-5xl mx-auto">
        <div className="h-6 w-24 bg-muted rounded"></div>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="aspect-square bg-muted rounded-xl"></div>
          <div className="space-y-4">
            <div className="h-10 w-3/4 bg-muted rounded"></div>
            <div className="h-8 w-1/4 bg-muted rounded"></div>
            <div className="h-4 w-full bg-muted rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (isError || !product) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold mb-2 text-destructive">Product not found</h2>
        <Link href="/">
          <Button variant="outline">Back to Products</Button>
        </Link>
      </div>
    );
  }

  const catName = product.category_data?.name.toLowerCase() || "";
  let query = "product";
  if (catName.includes("book")) query = "books";
  if (catName.includes("electronic") || catName.includes("tech")) query = "electronics";
  if (catName.includes("fashion") || catName.includes("clothes")) query = "fashion";
  const imgSrc = `https://picsum.photos/seed/${product.id}/800/800`;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <Link href="/" className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-foreground">
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Products
      </Link>

      <div className="grid md:grid-cols-2 gap-10">
        {/* Left: Image (Placeholder) */}
        <div className="relative aspect-square rounded-xl overflow-hidden border bg-muted flex-center">
          <div className="absolute inset-0 flex items-center justify-center text-muted-foreground bg-secondary/50 -z-10">
            <span className="text-6xl font-bold opacity-20">{product.name[0]}</span>
          </div>
          <img src={imgSrc} alt={product.name} className="object-cover w-full h-full shadow-inner" />
        </div>

        {/* Right: Details */}
        <div className="flex flex-col">
          <div className="mb-2 flex gap-2">
            {product.category_data && (
              <Badge variant="secondary">{product.category_data.name}</Badge>
            )}
            {product.detail_type && (
              <Badge variant="outline" className="capitalize">{product.detail_type}</Badge>
            )}
          </div>
          
          <h1 className="text-3xl font-bold tracking-tight mb-2">{product.name}</h1>
          <p className="text-3xl font-bold text-primary mb-6">${formatMoney(product.price)}</p>

          {/* Dynamic Details based on Category */}
          <div className="space-y-4 mb-8">
            <h3 className="text-lg font-semibold border-b pb-2">Specifications</h3>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 text-sm">
              <div className="flex flex-col">
                <dt className="text-muted-foreground">Stock Available</dt>
                <dd className="font-medium">{product.stock} units</dd>
              </div>

              {product.book && (
                <>
                  <div className="flex flex-col"><dt className="text-muted-foreground">Author</dt><dd className="font-medium">{product.book.author}</dd></div>
                  <div className="flex flex-col"><dt className="text-muted-foreground">Publisher</dt><dd className="font-medium">{product.book.publisher}</dd></div>
                  <div className="flex flex-col"><dt className="text-muted-foreground">ISBN</dt><dd className="font-medium">{product.book.isbn}</dd></div>
                </>
              )}
              {product.electronics && (
                <>
                  <div className="flex flex-col"><dt className="text-muted-foreground">Brand</dt><dd className="font-medium">{product.electronics.brand}</dd></div>
                  <div className="flex flex-col"><dt className="text-muted-foreground">Warranty</dt><dd className="font-medium">{product.electronics.warranty} months</dd></div>
                </>
              )}
              {product.fashion && (
                <>
                  <div className="flex flex-col"><dt className="text-muted-foreground">Size</dt><dd className="font-medium uppercase">{product.fashion.size}</dd></div>
                  <div className="flex flex-col"><dt className="text-muted-foreground">Color</dt><dd className="font-medium capitalize">{product.fashion.color}</dd></div>
                </>
              )}
            </dl>
          </div>

          <div className="mt-auto space-y-4 pt-6 border-t border-border">
            {product.stock > 0 ? (
              <>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium">Quantity:</span>
                  <div className="flex items-center border rounded-md">
                    <Button variant="ghost" size="icon" onClick={() => setQuantity(Math.max(1, quantity - 1))}>
                      <Minus className="w-4 h-4" />
                    </Button>
                    <span className="w-10 text-center text-sm font-medium">{quantity}</span>
                    <Button variant="ghost" size="icon" onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}>
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <Button 
                    size="lg" 
                    className="flex-1 text-base h-12" 
                    disabled={addMutation.isPending}
                    onClick={() => addMutation.mutate()}
                  >
                    <ShoppingCart className="w-5 h-5 mr-2" />
                    {addMutation.isPending ? "Adding..." : "Add to Cart"}
                  </Button>
                </div>
                {addMsg && (
                  <p className={`text-sm font-medium ${addMsg.includes("success") ? "text-green-600" : "text-destructive"}`}>
                    {addMsg}
                  </p>
                )}
              </>
            ) : (
              <Button size="lg" variant="secondary" className="w-full h-12 cursor-not-allowed" disabled>
                Out of Stock
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
