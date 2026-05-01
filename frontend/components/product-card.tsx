"use client";

import Link from "next/link";
import { Product } from "@/types";
import { Card, CardContent, CardFooter } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { getProductImageQuery } from "@/lib/product-types";
import { useAuthStore } from "@/lib/store";
import { trackBehaviorEvent } from "@/lib/ai";

export function ProductCard({ product }: { product: Product }) {
  const { user } = useAuthStore();
  const imageQuery = getProductImageQuery(product.detail_type, product.category_data?.name);
  const seedBase = `${product.id}-${imageQuery}`;
  const imgSrc = `https://picsum.photos/seed/${seedBase}/400/300`;

  const handleProductClick = () => {
    void trackBehaviorEvent({
      userId: user?.id,
      action: "click",
      productId: product.id,
    });
  };

  return (
    <Card className="overflow-hidden flex flex-col hover:shadow-lg transition-all duration-300">
      <Link href={`/products/${product.id}`} className="block relative aspect-video overflow-hidden bg-muted" onClick={handleProductClick}>
        {/* Fallback pattern for when Unsplash resolves */}
        <div className="absolute inset-0 flex items-center justify-center text-muted-foreground bg-secondary/50">
          <span className="text-xl font-bold opacity-30">{product.name[0]}</span>
        </div>
        <img
          src={imgSrc}
          alt={product.name}
          className="object-cover w-full h-full relative z-10 transition-transform hover:scale-105 duration-300"
          loading="lazy"
        />
      </Link>
      <CardContent className="p-4 flex-1">
        <div className="flex justify-between items-start gap-2 mb-2">
          <Link href={`/products/${product.id}`} className="font-semibold line-clamp-2 hover:text-primary transition-colors" onClick={handleProductClick}>
            {product.name}
          </Link>
          <span className="font-bold whitespace-nowrap text-lg text-primary">${product.price.toFixed(2)}</span>
        </div>
        <div className="flex items-center gap-2 mt-2">
          {product.category_data && (
            <Badge variant="secondary" className="font-normal">{product.category_data.name}</Badge>
          )}
          {product.stock <= 5 && product.stock > 0 && (
            <Badge variant="warning" className="font-normal">Low Stock</Badge>
          )}
          {product.stock === 0 && (
            <Badge variant="destructive" className="font-normal">Out of Stock</Badge>
          )}
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <Button asChild variant="outline" className="w-full">
          <Link href={`/products/${product.id}`} onClick={handleProductClick}>View Details</Link>
        </Button>
      </CardFooter>
    </Card>
  );
}
