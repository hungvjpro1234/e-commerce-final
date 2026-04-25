import axios from "axios";
import { useAuthStore } from "./store";

function isPublicCatalogRequest(url?: string, method?: string) {
  if ((method || "get").toLowerCase() !== "get" || !url) {
    return false;
  }

  return (
    url === "/products" ||
    url.startsWith("/products/") ||
    url === "/categories" ||
    url.startsWith("/categories/")
  );
}

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "/api",
  headers: {
    "Cache-Control": "no-cache",
    Pragma: "no-cache",
  },
});

api.interceptors.request.use((config) => {
  if (isPublicCatalogRequest(config.url, config.method)) {
    delete config.headers.Authorization;
    return config;
  }

  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
