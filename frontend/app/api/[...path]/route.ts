import { NextRequest } from "next/server";
import { cookies } from "next/headers";

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getFetchErrorCode(error: unknown): string | undefined {
  const anyError = error as any;
  return anyError?.cause?.code || anyError?.code;
}

function isTransientFetchError(error: unknown) {
  const code = getFetchErrorCode(error);
  return (
    code === "ECONNREFUSED" ||
    code === "ECONNRESET" ||
    code === "ETIMEDOUT" ||
    code === "EAI_AGAIN" ||
    code === "ENOTFOUND"
  );
}

async function fetchWithRetry(url: string, options: RequestInit, attempts = 6) {
  let lastError: unknown;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await fetch(url, options);
    } catch (error) {
      lastError = error;
      if (attempt === attempts || !isTransientFetchError(error)) {
        throw error;
      }
      const backoffMs = 200 * 2 ** (attempt - 1);
      await sleep(backoffMs);
    }
  }
  throw lastError;
}

const SERVICE_MAP: Record<string, string | undefined> = {
  auth: process.env.USER_SERVICE_URL,
  users: process.env.USER_SERVICE_URL,
  products: process.env.PRODUCT_SERVICE_URL,
  categories: process.env.PRODUCT_SERVICE_URL,
  cart: process.env.CART_SERVICE_URL,
  orders: process.env.ORDER_SERVICE_URL,
  payment: process.env.PAYMENT_SERVICE_URL,
  shipping: process.env.SHIPPING_SERVICE_URL,
  ai: process.env.AI_SERVICE_URL,
};

const COLLECTION_PATHS_REQUIRING_SLASH = new Set([
  "/users",
  "/products",
  "/categories",
  "/cart",
  "/orders",
]);

function isPublicCatalogRequest(prefix: string, method: string) {
  return method === "GET" && (prefix === "products" || prefix === "categories");
}

function trimTrailingSlashes(value: string) {
  return value.replace(/\/+$/, "");
}

function isGatewayApiBaseUrl(baseUrl: string) {
  return /\/api\/?$/.test(baseUrl);
}

function buildGatewayTargetPath(pathArray: string[]) {
  const [prefix, ...rest] = pathArray;
  const suffix = rest.length > 0 ? `/${rest.join("/")}` : "";

  switch (prefix) {
    case "auth":
      return `/users/auth${suffix}`;
    case "users":
      return `/users/users${suffix || "/"}`;
    case "products":
      return `/products/products${suffix || "/"}`;
    case "categories":
      return `/categories${suffix || "/"}`;
    case "cart":
      return `/cart${suffix || "/"}`;
    case "orders":
      return `/orders${suffix || "/"}`;
    case "payment":
      return `/payment${suffix || "/"}`;
    case "shipping":
      return `/shipping${suffix || "/"}`;
    case "ai":
      return `/ai${suffix || "/"}`;
    default:
      return `/${pathArray.join("/")}`;
  }
}

function normalizeTargetPath(pathArray: string[]) {
  const [prefix, ...rest] = pathArray;
  const normalizedPath = prefix === "ai"
    ? `/${rest.join("/")}`
    : `/${pathArray.join("/")}`;

  if (COLLECTION_PATHS_REQUIRING_SLASH.has(normalizedPath)) {
    return `${normalizedPath}/`;
  }

  return normalizedPath === "/" ? normalizedPath : normalizedPath.replace(/\/+$/, "");
}

async function handleProxy(req: NextRequest, { params }: { params: { path: string[] } }) {
  const pathArray = params.path;
  if (!pathArray || pathArray.length === 0) {
    return new Response("Not found", { status: 404 });
  }

  const prefix = pathArray[0];
  const baseUrl = SERVICE_MAP[prefix];

  if (!baseUrl) {
    console.error(`[Proxy] No service mapped for prefix: ${prefix}`);
    return new Response(`Service not found for /${prefix}`, { status: 404 });
  }

  const normalizedBaseUrl = trimTrailingSlashes(baseUrl);
  const targetPath = isGatewayApiBaseUrl(baseUrl)
    ? buildGatewayTargetPath(pathArray)
    : normalizeTargetPath(pathArray);
  const searchParams = req.nextUrl.search;
  const targetUrl = `${normalizedBaseUrl}${targetPath}${searchParams}`;

  try {
    const headers = new Headers(req.headers);
    // Remove host header to prevent issues when forwarding
    headers.delete("host");
    if (isPublicCatalogRequest(prefix, req.method)) {
      headers.delete("authorization");
    }

    // Inject Auth token directly from HTTP-only cookie if available
    const cookieStore = cookies();
    const token = cookieStore.get("auth_token")?.value;
    if (token && !isPublicCatalogRequest(prefix, req.method)) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const options: RequestInit = {
      method: req.method,
      headers: headers,
      // Follow backend slash-normalization redirects on the server so
      // the browser always receives the final API payload instead of
      // being redirected to a frontend HTML page.
      redirect: "follow",
    };

    if (["POST", "PUT", "PATCH", "DELETE"].includes(req.method)) {
      options.body = await req.arrayBuffer();
    }

    console.log(`[Proxy] ${req.method} ${targetUrl}`);
    const response = await fetchWithRetry(targetUrl, options);

    // Filter headers being sent back to the client
    const responseHeaders = new Headers(response.headers);
    responseHeaders.delete("transfer-encoding");
    responseHeaders.delete("content-encoding");
    responseHeaders.delete("location");
    responseHeaders.set("Cache-Control", "no-store");

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error("[Proxy Error]:", error);
    return new Response(JSON.stringify({ detail: "Gateway Error", error: String(error) }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }
}

export const GET = handleProxy;
export const POST = handleProxy;
export const PUT = handleProxy;
export const PATCH = handleProxy;
export const DELETE = handleProxy;
