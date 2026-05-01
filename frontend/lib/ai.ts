"use client";

import api from "@/lib/api";
import type {
  BehaviorAction,
  ChatbotResponse,
  RecommendationResponse,
} from "@/types";

interface RecommendationParams {
  userId: number;
  limit?: number;
  query?: string;
}

interface ChatbotRequest {
  userId?: number;
  message: string;
}

interface TrackBehaviorParams {
  userId?: number | null;
  action: BehaviorAction;
  productId?: number;
  queryText?: string;
}

export async function fetchRecommendations({
  userId,
  limit = 4,
  query,
}: RecommendationParams): Promise<RecommendationResponse> {
  const response = await api.get("/ai/recommend", {
    params: {
      user_id: userId,
      limit,
      query: query || undefined,
    },
  });

  return response.data;
}

export async function sendChatbotMessage({
  userId,
  message,
}: ChatbotRequest): Promise<ChatbotResponse> {
  const response = await api.post("/ai/chatbot", {
    user_id: userId,
    message,
  });

  return response.data;
}

export async function trackBehaviorEvent({
  userId,
  action,
  productId,
  queryText,
}: TrackBehaviorParams) {
  if (!userId) {
    return null;
  }

  try {
    const response = await api.post("/ai/behavior", {
      user_id: userId,
      action,
      product_id: productId,
      query_text: queryText,
    });

    return response.data;
  } catch (error) {
    console.error(`[AI] Failed to track ${action} event`, error);
    return null;
  }
}
