"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { ArrowLeft, Bot, MessageSquare, SendHorizonal, Sparkles } from "lucide-react";
import { sendChatbotMessage, trackBehaviorEvent } from "@/lib/ai";
import { useAuthStore } from "@/lib/store";
import { ChatbotResponse } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

interface ConversationTurn {
  id: string;
  role: "user" | "assistant";
  message: string;
  response?: ChatbotResponse;
}

const QUICK_PROMPTS = [
  "Tôi cần laptop giá rẻ để học và làm việc",
  "Gợi ý sách lập trình dễ bắt đầu",
  "Tư vấn quà tặng thời trang đơn giản",
];

function formatMoney(value: number) {
  return `$${value.toFixed(2)}`;
}

export default function ChatbotPage() {
  const { user } = useAuthStore();
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState<ConversationTurn[]>([]);

  const chatbotMutation = useMutation({
    mutationFn: async (nextMessage: string) =>
      sendChatbotMessage({
        userId: user?.id,
        message: nextMessage,
      }),
    onSuccess: (response, prompt) => {
      setConversation((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          message: response.answer,
          response,
        },
      ]);

      void trackBehaviorEvent({
        userId: user?.id,
        action: "search",
        queryText: prompt,
      });
    },
    onError: () => {
      setConversation((current) => [
        ...current,
        {
          id: `assistant-error-${Date.now()}`,
          role: "assistant",
          message: "AI service is temporarily unavailable. Please try another product question in a moment.",
        },
      ]);
    },
  });

  const submitMessage = (nextMessage: string) => {
    const trimmedMessage = nextMessage.trim();
    if (!trimmedMessage || chatbotMutation.isPending) {
      return;
    }

    setConversation((current) => [
      ...current,
      {
        id: `user-${Date.now()}`,
        role: "user",
        message: trimmedMessage,
      },
    ]);
    setMessage("");
    chatbotMutation.mutate(trimmedMessage);
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    submitMessage(message);
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Link href="/" className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" />
        Back to storefront
      </Link>

      <section className="grid gap-6 lg:grid-cols-[0.72fr_1.28fr]">
        <Card className="border-border/70 bg-gradient-to-br from-amber-50 via-white to-slate-50">
          <CardHeader className="space-y-3">
            <Badge className="w-fit">RAG + Recommendation</Badge>
            <CardTitle className="text-2xl">AI Product Advisor</CardTitle>
            <p className="text-sm text-muted-foreground">
              Chatbot này lấy grounded context từ Phase 8 và có thể boost bằng tín hiệu recommendation nếu bạn đã đăng nhập.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-2xl border bg-background/80 p-4 text-sm">
              <div className="mb-2 flex items-center gap-2 font-medium">
                <Sparkles className="h-4 w-4 text-amber-500" />
                Quick prompts
              </div>
              <div className="flex flex-wrap gap-2">
                {QUICK_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    className="rounded-full border px-3 py-1.5 text-left text-xs transition hover:border-primary hover:text-primary"
                    onClick={() => submitMessage(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border bg-slate-950 p-4 text-slate-100">
              <div className="mb-2 flex items-center gap-2 text-sm font-medium">
                <Bot className="h-4 w-4 text-amber-300" />
                Runtime notes
              </div>
              <ul className="space-y-2 text-sm text-slate-300">
                <li>{user ? `Personalization active for user #${user.id}` : "Anonymous mode uses retrieval and fallback ranking."}</li>
                <li>Answer trả về kèm product suggestions và retrieved context.</li>
                <li>Click vào suggestion vẫn quay lại product page hiện có của storefront.</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/70">
          <CardHeader className="border-b">
            <CardTitle className="flex items-center gap-2 text-xl">
              <MessageSquare className="h-5 w-5 text-primary" />
              Chatbot console
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 p-5">
            <div className="max-h-[34rem] space-y-4 overflow-y-auto rounded-2xl bg-muted/30 p-4">
              {conversation.length === 0 ? (
                <div className="rounded-2xl border border-dashed bg-background p-6 text-sm text-muted-foreground">
                  Hỏi về laptop, sách lập trình, thời trang hoặc quà tặng để xem grounded answer và product suggestions.
                </div>
              ) : (
                conversation.map((turn) => (
                  <div key={turn.id} className={`space-y-3 ${turn.role === "user" ? "ml-auto max-w-2xl" : "mr-auto max-w-3xl"}`}>
                    <div
                      className={`rounded-2xl px-4 py-3 text-sm ${
                        turn.role === "user"
                          ? "bg-slate-950 text-slate-50"
                          : "border bg-background text-foreground"
                      }`}
                    >
                      {turn.message}
                    </div>

                    {turn.response ? (
                      <div className="space-y-3 rounded-2xl border bg-background p-4">
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge variant="secondary">query_type: {turn.response.query_type}</Badge>
                          <Badge variant="outline">{turn.response.products.length} products</Badge>
                        </div>

                        {turn.response.products.length > 0 ? (
                          <div className="grid gap-3 md:grid-cols-2">
                            {turn.response.products.map((product) => (
                              <Link
                                key={product.id}
                                href={`/products/${product.id}`}
                                className="rounded-xl border p-3 transition hover:border-primary hover:shadow-sm"
                                onClick={() => {
                                  void trackBehaviorEvent({
                                    userId: user?.id,
                                    action: "click",
                                    productId: product.id,
                                  });
                                }}
                              >
                                <div className="flex items-start justify-between gap-3">
                                  <div>
                                    <p className="font-semibold">{product.name}</p>
                                    <p className="text-xs text-muted-foreground">{product.category}</p>
                                  </div>
                                  <Badge>{formatMoney(product.price)}</Badge>
                                </div>
                                <p className="mt-2 text-sm text-muted-foreground">{product.reason}</p>
                              </Link>
                            ))}
                          </div>
                        ) : null}

                        {turn.response.retrieved_context.length > 0 ? (
                          <div className="space-y-2">
                            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Retrieved context</p>
                            <div className="space-y-2 text-sm text-muted-foreground">
                              {turn.response.retrieved_context.map((context, index) => (
                                <div key={`${turn.id}-ctx-${index}`} className="rounded-xl bg-muted/50 px-3 py-2">
                                  {context}
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : null}
                      </div>
                    ) : null}
                  </div>
                ))
              )}

              {chatbotMutation.isPending ? (
                <div className="mr-auto max-w-3xl rounded-2xl border bg-background px-4 py-3 text-sm text-muted-foreground">
                  AI service is preparing a grounded answer...
                </div>
              ) : null}
            </div>

            <form onSubmit={handleSubmit} className="flex gap-3">
              <Input
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="Nhập câu hỏi tư vấn sản phẩm..."
                className="h-12"
              />
              <Button type="submit" className="h-12 px-5" disabled={chatbotMutation.isPending}>
                <SendHorizonal className="mr-2 h-4 w-4" />
                Send
              </Button>
            </form>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
