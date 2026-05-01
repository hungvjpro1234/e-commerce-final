"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { fetchRecommendations, trackBehaviorEvent } from "@/lib/ai";
import { useAuthStore } from "@/lib/store";
import { Product, RecommendationResponse } from "@/types";
import { ProductCard } from "@/components/product-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Search, Sparkles } from "lucide-react";

function formatMoney(value: number) {
  return `$${value.toFixed(2)}`;
}

export default function HomePage() {
  const { user } = useAuthStore();
  const [draftQuery, setDraftQuery] = useState("");
  const [activeQuery, setActiveQuery] = useState("");
  const recommendationUserId = user?.id ?? 999;

  const { data: products, isLoading, isError } = useQuery<Product[]>({
    queryKey: ["products"],
    queryFn: async () => {
      const res = await api.get("/products");
      return res.data;
    },
  });

  const {
    data: recommendations,
    isLoading: recommendationLoading,
  } = useQuery<RecommendationResponse>({
    queryKey: ["ai-recommendations", recommendationUserId, activeQuery],
    queryFn: async () =>
      fetchRecommendations({
        userId: recommendationUserId,
        limit: 4,
        query: activeQuery || undefined,
      }),
    staleTime: 60_000,
  });

  const normalizedFilter = draftQuery.trim().toLowerCase();
  const visibleProducts = products?.filter((product) => {
    if (!normalizedFilter) {
      return true;
    }

    const searchableText = [
      product.name,
      product.category_data?.name,
      product.detail_type,
      ...Object.values(product.detail || {}).map((value) => String(value)),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return searchableText.includes(normalizedFilter);
  });

  const handleSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextQuery = draftQuery.trim();
    setActiveQuery(nextQuery);

    if (nextQuery) {
      void trackBehaviorEvent({
        userId: user?.id,
        action: "search",
        queryText: nextQuery,
      });
    }
  };

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
      <section className="rounded-3xl border border-border/60 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 px-6 py-8 text-slate-50 shadow-xl">
        <div className="grid gap-8 lg:grid-cols-[1.35fr_0.65fr]">
          <div className="space-y-5">
            <Badge className="w-fit bg-white/10 text-white hover:bg-white/10">Phase 9 Frontend AI Demo</Badge>
            <div className="space-y-3">
              <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">AI tư vấn sản phẩm đã được nối trực tiếp vào storefront</h1>
              <p className="max-w-2xl text-sm text-slate-300 sm:text-base">
                Search sẽ làm mới hybrid recommendation, product detail ghi nhận hành vi, và chatbot lấy grounded answer từ AI service.
              </p>
            </div>

            <form onSubmit={handleSearch} className="flex flex-col gap-3 sm:flex-row">
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <Input
                  value={draftQuery}
                  onChange={(event) => setDraftQuery(event.target.value)}
                  placeholder="Ví dụ: budget laptop, programming book, fashion gift"
                  className="h-12 border-white/20 bg-white/10 pl-10 text-white placeholder:text-slate-400"
                />
              </div>
              <Button type="submit" className="h-12 bg-amber-400 px-6 text-slate-950 hover:bg-amber-300">
                Refresh AI Picks
              </Button>
            </form>

            <div className="flex flex-wrap gap-3 text-xs text-slate-300">
              <span>{user ? `Personalized for user #${user.id}` : "Cold-start mode with popularity fallback"}</span>
              <span>{activeQuery ? `AI query: ${activeQuery}` : "No active AI query yet"}</span>
            </div>
          </div>

          <Card className="border-white/10 bg-white/5 text-slate-50 shadow-none">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Sparkles className="h-5 w-5 text-amber-300" />
                Chat với AI Assistant
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-slate-300">
                Đặt câu hỏi tự nhiên để chatbot truy xuất RAG context và gợi ý sản phẩm phù hợp hơn.
              </p>
              <div className="space-y-2 text-sm text-slate-200">
                <div className="rounded-xl border border-white/10 bg-black/20 p-3">&quot;Tôi cần laptop giá rẻ để học tập&quot;</div>
                <div className="rounded-xl border border-white/10 bg-black/20 p-3">&quot;Tư vấn quà tặng thời trang dưới 100 đô&quot;</div>
              </div>
              <Button asChild variant="secondary" className="w-full bg-white text-slate-900 hover:bg-slate-100">
                <Link href="/chatbot">Open Chatbot Page</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">Gợi ý cho bạn</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Kết hợp LSTM, graph, RAG và popularity fallback qua `GET /recommend`.
            </p>
          </div>
          {recommendations?.sources_used?.length ? (
            <div className="flex flex-wrap justify-end gap-2">
              {recommendations.sources_used.map((source) => (
                <Badge key={source} variant="secondary">{source}</Badge>
              ))}
            </div>
          ) : null}
        </div>

        {recommendationLoading ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[1, 2, 3, 4].map((item) => (
              <div key={item} className="h-44 animate-pulse rounded-2xl border bg-muted" />
            ))}
          </div>
        ) : recommendations?.items?.length ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            {recommendations.items.map((item) => (
              <Card key={item.id} className="overflow-hidden border-border/70">
                <CardHeader className="space-y-3 pb-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <CardTitle className="text-lg leading-tight">{item.name}</CardTitle>
                      <p className="mt-1 text-sm text-muted-foreground">{item.category}</p>
                    </div>
                    <Badge>{formatMoney(item.price)}</Badge>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(item.source_scores)
                      .filter(([, score]) => score > 0)
                      .map(([source, score]) => (
                        <Badge key={source} variant="outline">
                          {source}: {score.toFixed(2)}
                        </Badge>
                      ))}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">{item.reason}</p>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{item.detail_type}</span>
                    <span>Score {item.score.toFixed(3)}</span>
                  </div>
                  <Button asChild className="w-full">
                    <Link
                      href={`/products/${item.id}`}
                      onClick={() => {
                        void trackBehaviorEvent({
                          userId: user?.id,
                          action: "click",
                          productId: item.id,
                        });
                      }}
                    >
                      View AI Pick
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed p-8 text-sm text-muted-foreground">
            AI recommendation chưa sẵn sàng. Hệ thống sẽ tiếp tục fallback về catalog hiện có.
          </div>
        )}
      </section>

      <section className="space-y-4">
        <div className="flex justify-between items-end gap-4">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Our Products</h2>
            <p className="text-muted-foreground mt-1">Discover the best items across multiple categories.</p>
          </div>
          <Badge variant="outline">{visibleProducts?.length ?? 0} products shown</Badge>
        </div>

        {visibleProducts && visibleProducts.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {visibleProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20 border rounded-xl border-dashed">
            <p className="text-lg text-muted-foreground">No products match the current search query.</p>
          </div>
        )}
      </section>
    </div>
  );
}
