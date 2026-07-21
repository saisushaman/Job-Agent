/** Tiny API client for talking to the Job-Agent backend. */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Join the API base URL with a path, tolerating leading/trailing slashes. */
export function apiUrl(path: string): string {
  const base = API_BASE_URL.replace(/\/+$/, "");
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${base}${suffix}`;
}

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  environment: string;
  database: string;
  time: string;
}

/** Fetch backend health. Throws on non-2xx. */
export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(apiUrl("/api/health"), { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Health check failed with status ${res.status}`);
  }
  return (await res.json()) as HealthResponse;
}
