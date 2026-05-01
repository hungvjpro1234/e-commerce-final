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

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken() {
  const { refreshToken, setAccessToken, logout } = useAuthStore.getState();

  if (!refreshToken) {
    logout();
    return null;
  }

  if (!refreshPromise) {
    refreshPromise = axios
      .post(`${process.env.NEXT_PUBLIC_API_URL || "/api"}/auth/refresh`, { refresh: refreshToken }, {
        headers: {
          "Cache-Control": "no-cache",
          Pragma: "no-cache",
        },
      })
      .then((response) => {
        const nextToken = response.data?.access;
        if (!nextToken || typeof nextToken !== "string") {
          throw new Error("Refresh endpoint did not return an access token.");
        }
        setAccessToken(nextToken);
        return nextToken;
      })
      .catch(() => {
        logout();
        return null;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
}

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

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {};
    const status = error.response?.status;
    const code = error.response?.data?.code;

    if (
      status === 401 &&
      code === "token_not_valid" &&
      !isPublicCatalogRequest(originalRequest.url, originalRequest.method) &&
      !(originalRequest as { _retry?: boolean })._retry
    ) {
      (originalRequest as { _retry?: boolean })._retry = true;
      const nextToken = await refreshAccessToken();
      if (nextToken) {
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${nextToken}`;
        return api(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
