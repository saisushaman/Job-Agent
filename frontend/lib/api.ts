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

async function sendJson<T>(
  path: string,
  method: "POST" | "PUT" | "PATCH",
  body?: unknown,
): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const b = await res.json();
      if (b?.detail) detail = typeof b.detail === "string" ? b.detail : detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
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

// --- Dashboard, jobs, matching, profile (Phase 6) ---

export interface TopMatch {
  job_id: number;
  title: string;
  company: string;
  overall_score: number;
  recommendation: string;
  region: string | null;
  eligibility: string | null;
}

export interface DashboardStats {
  total_jobs: number;
  analyzed: number;
  matched: number;
  pipeline: Record<string, number>;
  recommendations: Record<string, number>;
  regions: Record<string, number>;
  eligibility: Record<string, number>;
  usa_total: number;
  europe_total: number;
  sponsorship_us: Record<string, number>;
  visa_eu: Record<string, number>;
  top_matches: TopMatch[];
}

export interface JobListItem {
  id: number;
  title: string;
  company: string;
  country: string | null;
  city: string | null;
  url: string | null;
  description: string | null;
  analyzed: boolean;
  matched: boolean;
  region: string | null;
  eligibility: string | null;
  sponsorship_us: string | null;
  visa_support_eu: string | null;
  remote: boolean;
  match_score: number | null;
  recommendation: string | null;
}

export interface JobCreateInput {
  title: string;
  company: string;
  country?: string;
  city?: string;
  url?: string;
  description?: string;
}

export interface JobAnalysisResult {
  region: string;
  sponsorship_us: string | null;
  visa_support_eu: string | null;
  work_authorization_required: boolean;
  citizenship_required: boolean;
  citizenship_evidence: string | null;
  security_clearance_required: boolean;
  relocation: string;
  english_compatibility: string;
  technical_skills: string[];
  experience_years_min: number | null;
  experience_level: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  salary_period: string | null;
  sponsorship_evidence: string[];
  concerns: string[];
  summary: string;
  eligibility: string;
}

export interface MatchScores {
  technical: number;
  experience: number;
  sponsorship: number;
  location: number;
  language: number;
  relocation: number;
}

export interface MatchResult {
  scores: MatchScores;
  overall_score: number;
  recommendation: string;
  reasoning: string;
  matched_skills: string[];
  missing_skills: string[];
  sponsorship_evidence: string[];
  concerns: string[];
}

export interface JobDetail {
  job: {
    id: number;
    title: string;
    company: string;
    country: string | null;
    city: string | null;
    url: string | null;
    description: string | null;
  };
  analysis: {
    job_id: number;
    region: string;
    eligibility: string;
    citizenship_required: boolean;
    result: JobAnalysisResult;
  } | null;
  match: {
    job_id: number;
    overall_score: number;
    recommendation: string;
    result: MatchResult;
  } | null;
}

export interface Profile {
  id: number;
  full_name: string | null;
  headline: string | null;
  years_experience: number | null;
  skills: string[];
  languages: string[];
  current_location: string | null;
  current_country: string | null;
  preferred_regions: string[];
  needs_sponsorship: boolean;
  open_to_relocation: boolean;
  open_to_remote: boolean;
}

export const fetchStats = () => getJson<DashboardStats>("/api/dashboard/stats");

export function listJobs(filters: Record<string, string> = {}): Promise<JobListItem[]> {
  const params = new URLSearchParams(
    Object.entries(filters).filter(([, v]) => v !== "" && v != null),
  );
  const qs = params.toString();
  return getJson<JobListItem[]>(`/api/jobs${qs ? `?${qs}` : ""}`);
}

export const getJobDetail = (id: number) => getJson<JobDetail>(`/api/jobs/${id}/detail`);
export const createJob = (input: JobCreateInput) =>
  sendJson<{ id: number }>("/api/jobs", "POST", input);
export const analyzeJob = (id: number) =>
  sendJson<unknown>(`/api/jobs/${id}/analyze`, "POST");
export const matchJob = (id: number) =>
  sendJson<unknown>(`/api/jobs/${id}/match`, "POST");

export const getProfile = () => getJson<Profile>("/api/profile");
export const updateProfile = (patch: Partial<Profile>) =>
  sendJson<Profile>("/api/profile", "PUT", patch);

// --- Application tracker (Phase 7) ---

export const APPLICATION_STATUSES = [
  "DISCOVERED",
  "REVIEW",
  "APPROVED",
  "APPLICATION_READY",
  "APPLYING",
  "APPLIED",
  "RESPONSE_RECEIVED",
  "INTERVIEW",
  "OFFER",
  "REJECTED",
  "ON_HOLD",
  "NOT_ELIGIBLE",
] as const;

export interface ApplicationCard {
  id: number;
  job_id: number;
  job_title: string;
  job_company: string;
  status: string;
  match_score: number | null;
  recommendation: string | null;
  eligibility: string | null;
  applied_at: string | null;
  updated_at: string;
}

export interface ApplicationEvent {
  id: number;
  event_type: string;
  from_status: string | null;
  to_status: string | null;
  message: string | null;
  created_at: string;
}

export interface ApplicationDetail {
  id: number;
  job_id: number;
  job_title: string;
  job_company: string;
  status: string;
  notes: string | null;
  external_application_id: string | null;
  applied_at: string | null;
  resume_version_id: number | null;
  cover_letter: string | null;
  recruiter_name: string | null;
  recruiter_email: string | null;
  recruiter_notes: string | null;
  interview_at: string | null;
  rejection_reason: string | null;
  offer_details: string | null;
  offer_salary: number | null;
  created_at: string;
  updated_at: string;
  events: ApplicationEvent[];
}

export const listApplications = () =>
  getJson<ApplicationCard[]>("/api/applications");
export const getApplication = (id: number) =>
  getJson<ApplicationDetail>(`/api/applications/${id}`);
export const createApplication = (jobId: number) =>
  sendJson<ApplicationDetail>("/api/applications", "POST", { job_id: jobId });
export const updateApplication = (
  id: number,
  patch: Partial<Omit<ApplicationDetail, "id" | "events">>,
) => sendJson<ApplicationDetail>(`/api/applications/${id}`, "PATCH", patch);

// --- Resume tailoring (Phase 8) ---

export interface TailoredDocument {
  id: number;
  application_id: number;
  source_resume_version_id: number | null;
  status: string; // DRAFT | APPROVED
  approved_at: string | null;
  before_resume: string;
  tailored_resume: string;
  cover_letter: string;
  draft_answers: { question: string; answer: string }[];
  changes_summary: string[];
  created_at: string;
  updated_at: string;
}

export const generateTailored = (
  appId: number,
  req: { resume_version_id?: number; questions?: string[] } = {},
) => sendJson<TailoredDocument>(`/api/applications/${appId}/tailor`, "POST", req);

export async function getTailored(appId: number): Promise<TailoredDocument | null> {
  const res = await fetch(apiUrl(`/api/applications/${appId}/tailor`), {
    cache: "no-store",
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return (await res.json()) as TailoredDocument;
}

export const approveTailored = (appId: number) =>
  sendJson<TailoredDocument>(`/api/applications/${appId}/tailor/approve`, "POST");

export const tailorDocumentUrl = (
  appId: number,
  kind: "resume" | "cover_letter",
  fmt: "txt" | "md" | "docx",
) => apiUrl(`/api/applications/${appId}/tailor/document?kind=${kind}&fmt=${fmt}`);

// --- Email (Phase 9) ---

export const EMAIL_CATEGORIES = [
  "APPLICATION_CONFIRMATION",
  "RECRUITER_CONTACT",
  "INTERVIEW",
  "ASSESSMENT",
  "REJECTION",
  "OFFER",
  "FOLLOW_UP",
  "OTHER",
] as const;

export interface EmailProviderStatus {
  provider: string;
  configured: boolean;
  detail: string;
}

export interface EmailOut {
  id: number;
  external_id: string;
  sender: string;
  sender_email: string;
  subject: string;
  snippet: string;
  received_at: string | null;
  classified: boolean;
  category: string | null;
  confidence: number | null;
  needs_review: boolean;
  application_id: number | null;
  application_job_title: string | null;
}

export const emailStatus = () =>
  getJson<EmailProviderStatus>("/api/emails/status");
export const listEmails = (filters: Record<string, string> = {}) => {
  const qs = new URLSearchParams(
    Object.entries(filters).filter(([, v]) => v !== "" && v != null),
  ).toString();
  return getJson<EmailOut[]>(`/api/emails${qs ? `?${qs}` : ""}`);
};
export const syncEmails = () =>
  sendJson<{ provider: string; fetched: number; new: number }>(
    "/api/emails/sync",
    "POST",
  );
export const classifyEmails = () =>
  sendJson<{
    classified: number;
    needs_review: number;
    matched: number;
    status_updates: number;
  }>("/api/emails/classify", "POST");
export const patchEmail = (
  id: number,
  patch: { category?: string; application_id?: number | null; needs_review?: boolean },
) => sendJson<EmailOut>(`/api/emails/${id}`, "PATCH", patch);
