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

// --- Resumes (Phase 3) ---

export interface ResumeSummary {
  id: number;
  kind: string;
  name: string;
  version_count: number;
  latest_version_number: number | null;
}

export interface ResumeVersionSummary {
  id: number;
  version_number: number;
  original_filename: string;
  content_type: string | null;
  file_size: number;
  created_at: string;
}

export interface ResumeVersionDetail extends ResumeVersionSummary {
  parsed_text: string;
}

export interface ResumeDetail {
  id: number;
  kind: string;
  name: string;
  versions: ResumeVersionSummary[];
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path), { cache: "no-store" });
  if (!res.ok) throw new Error(`Request failed (${res.status}) for ${path}`);
  return (await res.json()) as T;
}

export const listResumes = () => getJson<ResumeSummary[]>("/api/resumes");
export const getResume = (id: number) => getJson<ResumeDetail>(`/api/resumes/${id}`);
export const getResumeVersion = (versionId: number) =>
  getJson<ResumeVersionDetail>(`/api/resumes/versions/${versionId}`);

export const resumeVersionDownloadUrl = (versionId: number) =>
  apiUrl(`/api/resumes/versions/${versionId}/download`);

/** Upload a resume file (PDF/DOCX/TXT) as a new version of a track. */
export async function uploadResumeVersion(
  resumeId: number,
  file: File,
): Promise<ResumeVersionDetail> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(apiUrl(`/api/resumes/${resumeId}/versions`), {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    let detail = `Upload failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return (await res.json()) as ResumeVersionDetail;
}
