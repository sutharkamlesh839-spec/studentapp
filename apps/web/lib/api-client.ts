export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function requestHeaders(init?: RequestInit): Headers {
  const headers = new Headers(init?.headers);
  const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
  if (!isFormData && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  return headers;
}

async function send(path: string, init?: RequestInit): Promise<Response> {
  return fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: requestHeaders(init),
  });
}

function formatApiDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => {
      if (!item || typeof item !== "object") return String(item);
      const value = item as { msg?: unknown; loc?: unknown[] };
      const message = typeof value.msg === "string" ? value.msg : "Invalid value";
      const location = Array.isArray(value.loc) ? value.loc.filter((part) => part !== "body").join(" → ") : "";
      return location ? `${location}: ${message}` : message;
    });
    return messages.filter(Boolean).join(". ");
  }
  if (detail && typeof detail === "object" && "message" in detail) {
    const message = (detail as { message?: unknown }).message;
    if (typeof message === "string") return message;
  }
  return "Please check the submitted details and try again.";
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let response = await send(path, init);

  // Access tokens are intentionally short-lived. Rotate the HttpOnly refresh
  // cookie once for ordinary API calls, without retrying auth endpoints.
  if (response.status === 401 && !path.includes("/auth/")) {
    const refresh = await send("/api/v1/auth/refresh", { method: "POST" });
    if (refresh.ok) response = await send(path, init);
  }

  if (!response.ok) {
    let message = "Something went wrong. Please try again.";
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (body.detail !== undefined) message = formatApiDetail(body.detail);
    } catch {
      // The API may return an empty body for a gateway error.
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
