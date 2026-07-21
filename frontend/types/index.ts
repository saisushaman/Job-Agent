/** Shared frontend types. Domain types (Job, Application, ...) are added in later phases. */

export type { HealthResponse } from "@/lib/api";

/** Application status lifecycle (see PROJECT_SPEC.md). Reference for later phases. */
export type ApplicationStatus =
  | "DISCOVERED"
  | "REVIEW"
  | "APPROVED"
  | "APPLICATION_READY"
  | "APPLYING"
  | "APPLIED"
  | "RESPONSE_RECEIVED"
  | "INTERVIEW"
  | "OFFER"
  | "REJECTED"
  | "ON_HOLD"
  | "NOT_ELIGIBLE";
