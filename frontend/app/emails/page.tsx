"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import Nav from "@/components/Nav";
import {
  EMAIL_CATEGORIES,
  classifyEmails,
  emailStatus,
  listEmails,
  patchEmail,
  syncEmails,
  type EmailOut,
  type EmailProviderStatus,
} from "@/lib/api";

const CAT_COLOR: Record<string, string> = {
  APPLICATION_CONFIRMATION: "bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300",
  RECRUITER_CONTACT: "bg-sky-100 text-sky-800 dark:bg-sky-900/50 dark:text-sky-300",
  INTERVIEW: "bg-purple-100 text-purple-800 dark:bg-purple-900/50 dark:text-purple-300",
  ASSESSMENT: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/50 dark:text-indigo-300",
  REJECTION: "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300",
  OFFER: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300",
  FOLLOW_UP: "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300",
  OTHER: "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300",
};

export default function EmailsPage() {
  const [status, setStatus] = useState<EmailProviderStatus | null>(null);
  const [emails, setEmails] = useState<EmailOut[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const refresh = useCallback(() => {
    listEmails(filters)
      .then(setEmails)
      .catch((e) => setError(String(e.message ?? e)));
  }, [filters]);

  useEffect(() => {
    emailStatus().then(setStatus).catch(() => {});
  }, []);
  useEffect(() => {
    refresh();
  }, [refresh]);

  async function run(kind: "sync" | "classify") {
    setError(null);
    setMsg(null);
    setBusy(kind);
    try {
      if (kind === "sync") {
        const r = await syncEmails();
        setMsg(`Synced ${r.new} new email(s) (${r.fetched} fetched).`);
      } else {
        const r = await classifyEmails();
        setMsg(
          `Classified ${r.classified}; matched ${r.matched}; ${r.needs_review} need review; ${r.status_updates} status update(s).`,
        );
      }
      refresh();
    } catch (e) {
      setError(String((e as Error).message ?? e));
    } finally {
      setBusy(null);
    }
  }

  async function override(id: number, category: string) {
    try {
      await patchEmail(id, { category });
      refresh();
    } catch (e) {
      setError(String((e as Error).message ?? e));
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <Nav />
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Emails</h1>
        <div className="flex gap-2">
          <button
            onClick={() => run("sync")}
            disabled={busy !== null}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100 disabled:opacity-50 dark:border-slate-600 dark:hover:bg-slate-800"
          >
            {busy === "sync" ? "Syncing…" : "Sync"}
          </button>
          <button
            onClick={() => run("classify")}
            disabled={busy !== null}
            className="rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-50 dark:bg-white dark:text-slate-900"
          >
            {busy === "classify" ? "Classifying…" : "Classify"}
          </button>
        </div>
      </div>

      {status && (
        <div
          className={`mb-4 rounded-lg border px-4 py-2 text-sm ${
            status.configured
              ? "border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
              : "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-300"
          }`}
        >
          <span className="font-medium">Provider: {status.provider}</span> — {status.detail}
        </div>
      )}

      {msg && (
        <div className="mb-4 rounded-lg border border-emerald-300 bg-emerald-50 px-4 py-2 text-sm text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">
          {msg}
        </div>
      )}
      {error && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="mb-4 flex flex-wrap gap-2">
        <select
          onChange={(e) => setFilters((f) => ({ ...f, category: e.target.value }))}
          className="rounded-md border border-slate-300 bg-transparent px-3 py-1.5 text-sm dark:border-slate-600"
        >
          <option value="">All categories</option>
          {EMAIL_CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c.replace(/_/g, " ")}
            </option>
          ))}
        </select>
        <label className="flex items-center gap-1.5 text-sm text-slate-600 dark:text-slate-300">
          <input
            type="checkbox"
            onChange={(e) =>
              setFilters((f) => ({ ...f, needs_review: e.target.checked ? "true" : "" }))
            }
          />
          Needs review only
        </label>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
        <table className="w-full min-w-[820px] text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500 dark:bg-slate-800">
            <tr>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Category</th>
              <th className="px-4 py-3">Confidence</th>
              <th className="px-4 py-3">Matched</th>
              <th className="px-4 py-3">Override</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
            {emails.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                  No emails. Click Sync, then Classify.
                </td>
              </tr>
            ) : (
              emails.map((e) => (
                <tr key={e.id} className="bg-white dark:bg-slate-900/40">
                  <td className="px-4 py-3">
                    <div className="font-medium">{e.subject || "(no subject)"}</div>
                    <div className="text-xs text-slate-500">{e.sender_email}</div>
                  </td>
                  <td className="px-4 py-3">
                    {e.category ? (
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-semibold ${CAT_COLOR[e.category] ?? CAT_COLOR.OTHER}`}
                      >
                        {e.category.replace(/_/g, " ")}
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400">unclassified</span>
                    )}
                    {e.needs_review && (
                      <span className="ml-2 text-[10px] font-semibold uppercase text-amber-600">
                        needs review
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-slate-600 dark:text-slate-300">
                    {e.confidence != null ? `${Math.round(e.confidence * 100)}%` : "—"}
                  </td>
                  <td className="px-4 py-3">
                    {e.application_id ? (
                      <Link
                        href={`/applications/${e.application_id}`}
                        className="text-indigo-600 hover:underline"
                      >
                        {e.application_job_title ?? `#${e.application_id}`}
                      </Link>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={e.category ?? ""}
                      onChange={(ev) => override(e.id, ev.target.value)}
                      className="rounded-md border border-slate-300 bg-transparent px-2 py-1 text-xs dark:border-slate-600"
                    >
                      <option value="" disabled>
                        set…
                      </option>
                      {EMAIL_CATEGORIES.map((c) => (
                        <option key={c} value={c}>
                          {c.replace(/_/g, " ")}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs text-slate-400">
        Classification runs locally on Qwen3. Low-confidence emails are flagged “needs
        review”. The app never deletes email; Gmail (when configured) is read-only.
      </p>
    </main>
  );
}
