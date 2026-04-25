"use client";

import Link from "next/link";
import { Product } from "@/types";
import { Card, CardContent, CardFooter } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";

export function ProductCard({ product }: { product: Product }) {
  // Determine an appropriate unsplash placeholder based on category name
  const catName = product.category_data?.name.toLowerCase() || "";
  let query = "product";
  if (catName.includes("book")) query = "books";
  if (catName.includes("electronic") || catName.includes("tech")) query = "electronics";
  if (catName.includes("fashion") || catName.includes("clothes")) query = "fashion";

  // Use a predictable pseudo-random image to avoid layout shifts if it re-renders
  const imgSrc = `https://picsum.photos/seed/${product.id + catName.charCodeAt(0)}/400/300`;

  return (
    <Card className="overflow-hidden flex flex-col hover:shadow-lg transition-all duration-300">
      <Link href={`/products/${product.id}`} className="block relative aspect-video overflow-hidden bg-muted">
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
          <Link href={`/products/${product.id}`} className="font-semibold line-clamp-2 hover:text-primary transition-colors">
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
        <Link href={`/products/${product.id}`} className="w-full">
          <Button variant="outline" className="w-full">View Details</Button>
        </Link>
      </CardFooter>
    </Card>
  );
}
