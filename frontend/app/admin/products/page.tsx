"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { ManagementShell } from "@/components/management-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Product, Category, ProductFormValues } from "@/types";
import { formatMoney } from "@/lib/admin";

const adminNav = [
  { href: "/admin", label: "Overview", description: "Admin landing page and quick links." },
  { href: "/admin/products", label: "Products", description: "Manage catalog products and detail payloads." },
  { href: "/admin/categories", label: "Categories", description: "Manage catalog categories." },
  { href: "/admin/users", label: "Users", description: "Manage user accounts and roles." },
  { href: "/admin/orders", label: "Orders", description: "Review and update order statuses." },
  { href: "/admin/shipping", label: "Shipping", description: "Review and update shipment statuses." },
];

const defaultForm: ProductFormValues = {
  name: "",
  price: 0,
  stock: 0,
  category: 0,
  detail_type: "book",
  detail: { author: "", publisher: "", isbn: "" },
};

function getDetailDraft(type: ProductFormValues["detail_type"], product?: Product): Record<string, string | number> {
  if (type === "book") {
    return {
      author: product?.book?.author || "",
      publisher: product?.book?.publisher || "",
      isbn: product?.book?.isbn || "",
    };
  }
  if (type === "electronics") {
    return {
      brand: product?.electronics?.brand || "",
      warranty: product?.electronics?.warranty || 12,
    };
  }
  return {
    size: product?.fashion?.size || "",
    color: product?.fashion?.color || "",
  };
}

export default function AdminProductsPage() {
  const queryClient = useQueryClient();
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [form, setForm] = useState<ProductFormValues>(defaultForm);

  const { data: products } = useQuery<Product[]>({
    queryKey: ["admin-products"],
    queryFn: async () => (await api.get("/products")).data,
  });

  const { data: categories } = useQuery<Category[]>({
    queryKey: ["admin-categories"],
    queryFn: async () => (await api.get("/categories")).data,
  });

  const saveMutation = useMutation({
    mutationFn: async (payload: ProductFormValues) => {
      if (editingProduct) {
        return (await api.patch(`/products/${editingProduct.id}`, payload)).data;
      }
      return (await api.post("/products", payload)).data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-products"] });
      setEditingProduct(null);
      setForm(defaultForm);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (productId: number) => api.delete(`/products/${productId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-products"] }),
  });

  const detailFields = useMemo(() => {
    if (form.detail_type === "book") return ["author", "publisher", "isbn"];
    if (form.detail_type === "electronics") return ["brand", "warranty"];
    return ["size", "color"];
  }, [form.detail_type]);

  return (
    <ManagementShell
      title="Admin Product Management"
      description="Create, update, and delete products with category and detail payload support."
      navTitle="Admin Navigation"
      navItems={adminNav}
    >
      <div className="grid gap-6 xl:grid-cols-[420px_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <CardTitle>{editingProduct ? `Edit Product #${editingProduct.id}` : "Create Product"}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Product name" />
            <div className="grid gap-4 md:grid-cols-2">
              <Input
                type="number"
                value={form.price}
                onChange={(e) => setForm({ ...form, price: Number(e.target.value) })}
                placeholder="Price"
              />
              <Input
                type="number"
                value={form.stock}
                onChange={(e) => setForm({ ...form, stock: Number(e.target.value) })}
                placeholder="Stock"
              />
            </div>
            <select
              className="flex h-9 w-full rounded-md border border-border bg-transparent px-3 py-1 text-sm shadow-sm"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: Number(e.target.value) })}
            >
              <option value={0}>Select category</option>
              {(categories || []).map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            <select
              className="flex h-9 w-full rounded-md border border-border bg-transparent px-3 py-1 text-sm shadow-sm"
              value={form.detail_type}
              onChange={(e) =>
                setForm({
                  ...form,
                  detail_type: e.target.value as ProductFormValues["detail_type"],
                  detail: getDetailDraft(e.target.value as ProductFormValues["detail_type"], editingProduct || undefined),
                })
              }
            >
              <option value="book">Book</option>
              <option value="electronics">Electronics</option>
              <option value="fashion">Fashion</option>
            </select>
            <div className="grid gap-4">
              {detailFields.map((field) => (
                <Input
                  key={field}
                  type={field === "warranty" ? "number" : "text"}
                  value={String(form.detail[field] ?? "")}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      detail: {
                        ...form.detail,
                        [field]: field === "warranty" ? Number(e.target.value) : e.target.value,
                      },
                    })
                  }
                  placeholder={field}
                />
              ))}
            </div>
            <div className="flex gap-2">
              <Button
                onClick={() => saveMutation.mutate(form)}
                disabled={!form.name || !form.category || saveMutation.isPending}
              >
                {saveMutation.isPending ? "Saving..." : editingProduct ? "Update Product" : "Create Product"}
              </Button>
              {editingProduct && (
                <Button variant="outline" onClick={() => { setEditingProduct(null); setForm(defaultForm); }}>
                  Cancel
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Catalog Products</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {(products || []).map((product) => (
              <div key={product.id} className="rounded-lg border p-4">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="font-semibold">{product.name}</span>
                      {product.category_data && <Badge variant="secondary">{product.category_data.name}</Badge>}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      ${formatMoney(product.price)} · Stock {product.stock}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setEditingProduct(product);
                        const detailType = product.book ? "book" : product.electronics ? "electronics" : "fashion";
                        setForm({
                          name: product.name,
                          price: product.price,
                          stock: product.stock,
                          category: product.category,
                          detail_type: detailType,
                          detail: getDetailDraft(detailType, product),
                        });
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      onClick={() => deleteMutation.mutate(product.id)}
                      disabled={deleteMutation.isPending}
                    >
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
