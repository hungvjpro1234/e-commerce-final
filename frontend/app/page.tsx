"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { Product } from "@/types";
import { ProductCard } from "@/components/product-card";

export default function HomePage() {
  const { data: products, isLoading, isError } = useQuery<Product[]>({
    queryKey: ["products"],
    queryFn: async () => {
      const res = await api.get("/products");
      return res.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <div className="h-10 w-48 bg-muted animate-pulse rounded-md"></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="rounded-xl border bg-card text-card-foreground shadow h-[350px] animate-pulse flex flex-col">
              <div className="bg-muted h-[200px] w-full"></div>
              <div className="p-4 space-y-3">
                <div className="h-5 bg-muted rounded w-3/4"></div>
                <div className="h-4 bg-muted rounded w-1/4"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (isError || !products) {
    return (
      <div className="text-center py-20">
        <h2 className="text-2xl font-bold mb-2 text-destructive">Failed to load products</h2>
        <p className="text-muted-foreground">Please check if the backend services are running.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Our Products</h1>
          <p className="text-muted-foreground mt-1">Discover the best items across multiple categories.</p>
        </div>
      </div>

      {products.length === 0 ? (
        <div className="text-center py-20 border rounded-xl border-dashed">
          <p className="text-lg text-muted-foreground">No products available at the moment.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
