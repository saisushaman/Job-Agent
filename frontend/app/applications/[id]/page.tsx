"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import Nav from "@/components/Nav";
import {
  APPLICATION_STATUSES,
  getApplication,
  updateApplication,
  type ApplicationDetail,
} from "@/lib/api";

function dtLocal(value: string | null): string {
  return value ? value.slice(0, 16) : "";
}

export default function ApplicationDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const [app, setApp] = useState<ApplicationDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getApplication(id)
      .then(setApp)
      .catch((e) => setError(String(e.message ?? e)));
  }, [id]);

  function set<K extends keyof ApplicationDetail>(key: K, value: ApplicationDetail[K]) {
    setApp((a) => (a ? { ...a, [key]: value } : a));
    setSaved(false);
  }

  async function save(patch: Partial<ApplicationDetail>) {
    setError(null);
    setSaving(true);
    try {
      setApp(await updateApplication(id, patch));
      setSaved(true);
    } catch (e) {
      setError(String((e as Error).message ?? e));
      // reload to reflect true state (e.g. blocked transition)
      getApplication(id).then(setApp).catch(() => {});
    } finally {
      setSaving(false);
    }
  }

  const input =
    "w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm dark:border-slate-600";
  const label = "mb-1 block text-xs font-medium uppercase text-slate-500";

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <Nav />
      <Link href="/applications" className="text-sm text-slate-500 hover:underline">
        ← Board
      </Link>

      {error && (
        <div className="my-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      {app && (
        <>
          <div className="mb-6 mt-2 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">{app.job_title}</h1>
              <p className="text-slate-500">
                {app.job_company} ·{" "}
                <Link href={`/jobs/${app.job_id}`} className="text-indigo-600 hover:underline">
                  view job
                </Link>
              </p>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={app.status}
                onChange={(e) => save({ status: e.target.value })}
                className={input + " w-auto"}
              >
                {APPLICATION_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              save({
                external_application_id: app.external_application_id,
                applied_at: app.applied_at,
                interview_at: app.interview_at,
                recruiter_name: app.recruiter_name,
                recruiter_email: app.recruiter_email,
                recruiter_notes: app.recruiter_notes,
                notes: app.notes,
                cover_letter: app.cover_letter,
                rejection_reason: app.rejection_reason,
                offer_details: app.offer_details,
                offer_salary: app.offer_salary,
                resume_version_id: app.resume_version_id,
              });
            }}
            className="grid gap-4 rounded-xl border border-slate-200 bg-white p-6 sm:grid-cols-2 dark:border-slate-700 dark:bg-slate-800"
          >
            <div>
              <label className={label}>Application ID (external)</label>
              <input
                className={input}
                value={app.external_application_id ?? ""}
                onChange={(e) => set("external_application_id", e.target.value)}
              />
            </div>
            <div>
              <label className={label}>Resume version ID</label>
              <input
                type="number"
                className={input}
                value={app.resume_version_id ?? ""}
                onChange={(e) =>
                  set(
                    "resume_version_id",
                    e.target.value === "" ? null : Number(e.target.value),
                  )
                }
              />
            </div>
            <div>
              <label className={label}>Applied at</label>
              <input
                type="datetime-local"
                className={input}
                value={dtLocal(app.applied_at)}
                onChange={(e) => set("applied_at", e.target.value || null)}
              />
            </div>
            <div>
              <label className={label}>Interview at</label>
              <input
                type="datetime-local"
                className={input}
                value={dtLocal(app.interview_at)}
                onChange={(e) => set("interview_at", e.target.value || null)}
              />
            </div>
            <div>
              <label className={label}>Recruiter name</label>
              <input
                className={input}
                value={app.recruiter_name ?? ""}
                onChange={(e) => set("recruiter_name", e.target.value)}
              />
            </div>
            <div>
              <label className={label}>Recruiter email</label>
              <input
                className={input}
                value={app.recruiter_email ?? ""}
                onChange={(e) => set("recruiter_email", e.target.value)}
              />
            </div>
            <div className="sm:col-span-2">
              <label className={label}>Notes</label>
              <textarea
                className={input + " min-h-20"}
                value={app.notes ?? ""}
                onChange={(e) => set("notes", e.target.value)}
              />
            </div>
            <div className="sm:col-span-2">
              <label className={label}>Cover letter</label>
              <textarea
                className={input + " min-h-24"}
                value={app.cover_letter ?? ""}
                onChange={(e) => set("cover_letter", e.target.value)}
              />
            </div>
            <div className="sm:col-span-2">
              <label className={label}>Rejection reason</label>
              <input
                className={input}
                value={app.rejection_reason ?? ""}
                onChange={(e) => set("rejection_reason", e.target.value)}
              />
            </div>
            <div>
              <label className={label}>Offer details</label>
              <input
                className={input}
                value={app.offer_details ?? ""}
                onChange={(e) => set("offer_details", e.target.value)}
              />
            </div>
            <div>
              <label className={label}>Offer salary</label>
              <input
                type="number"
                className={input}
                value={app.offer_salary ?? ""}
                onChange={(e) =>
                  set("offer_salary", e.target.value === "" ? null : Number(e.target.value))
                }
              />
            </div>
            <div className="flex items-center gap-3 sm:col-span-2">
              <button
                type="submit"
                disabled={saving}
                className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-white dark:text-slate-900"
              >
                {saving ? "Saving…" : "Save"}
              </button>
              {saved && <span className="text-sm text-emerald-600">Saved ✓</span>}
            </div>
          </form>

          <div className="mt-6 rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
              History
            </h2>
            <ul className="space-y-2">
              {app.events.map((e) => (
                <li key={e.id} className="flex gap-3 text-sm">
                  <span className="text-slate-400">
                    {new Date(e.created_at).toLocaleString()}
                  </span>
                  <span className="font-medium">
                    {e.event_type === "STATUS_CHANGE"
                      ? `${e.from_status ?? "—"} → ${e.to_status}`
                      : e.event_type}
                  </span>
                  {e.message && <span className="text-slate-500">{e.message}</span>}
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </main>
  );
}
