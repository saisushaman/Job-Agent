"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import Nav from "@/components/Nav";
import {
  EligibilityBadge,
  RecommendationBadge,
  ScoreBadge,
} from "@/components/badges";
import {
  analyzeJob,
  createJob,
  listJobs,
  matchJob,
  type JobCreateInput,
  type JobListItem,
} from "@/lib/api";

const EMPTY_FORM: JobCreateInput = {
  title: "",
  company: "",
  country: "",
  city: "",
  url: "",
  description: "",
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobListItem[]>([]);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [form, setForm] = useState<JobCreateInput>(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setJobs(await listJobs(filters));
    } catch (e) {
      setError(String((e as Error).message ?? e));
    }
  }, [filters]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setCreating(true);
    try {
      await createJob(form);
      setForm(EMPTY_FORM);
      setShowForm(false);
      await refresh();
    } catch (err) {
      setError(String((err as Error).message ?? err));
    } finally {
      setCreating(false);
    }
  }

  async function runAction(id: number, action: "analyze" | "match") {
    setError(null);
    setBusyId(id);
    try {
      if (action === "analyze") await analyzeJob(id);
      else await matchJob(id);
      await refresh();
    } catch (err) {
      setError(String((err as Error).message ?? err));
    } finally {
      setBusyId(null);
    }
  }

  const setFilter = (key: string, value: string) =>
    setFilters((f) => ({ ...f, [key]: value }));

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <Nav />

      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Jobs</h1>
        <button
          onClick={() => setShowForm((s) => !s)}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-white dark:text-slate-900"
        >
          {showForm ? "Cancel" : "Import job"}
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-6 grid gap-3 rounded-xl border border-slate-200 bg-white p-5 sm:grid-cols-2 dark:border-slate-700 dark:bg-slate-800"
        >
          {(["title", "company", "country", "city", "url"] as const).map((field) => (
            <input
              key={field}
              required={field === "title" || field === "company"}
              placeholder={field[0].toUpperCase() + field.slice(1)}
              value={(form[field] as string) ?? ""}
              onChange={(e) => setForm({ ...form, [field]: e.target.value })}
              className="rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm dark:border-slate-600"
            />
          ))}
          <textarea
            placeholder="Job description"
            value={form.description ?? ""}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="min-h-24 rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm sm:col-span-2 dark:border-slate-600"
          />
          <button
            type="submit"
            disabled={creating}
            className="w-fit rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {creating ? "Saving…" : "Save job"}
          </button>
        </form>
      )}

      {/* Filters */}
      <div className="mb-4 flex flex-wrap gap-2">
        <input
          placeholder="Search title/company…"
          onChange={(e) => setFilter("q", e.target.value)}
          className="rounded-md border border-slate-300 bg-transparent px-3 py-1.5 text-sm dark:border-slate-600"
        />
        <select
          onChange={(e) => setFilter("region", e.target.value)}
          className="rounded-md border border-slate-300 bg-transparent px-3 py-1.5 text-sm dark:border-slate-600"
        >
          <option value="">All regions</option>
          <option value="USA">USA</option>
          <option value="EUROPE">Europe</option>
          <option value="OTHER">Other</option>
        </select>
        <select
          onChange={(e) => setFilter("eligibility", e.target.value)}
          className="rounded-md border border-slate-300 bg-transparent px-3 py-1.5 text-sm dark:border-slate-600"
        >
          <option value="">All eligibility</option>
          <option value="ELIGIBLE">Eligible</option>
          <option value="REVIEW">Review</option>
          <option value="NOT_ELIGIBLE">Not eligible</option>
        </select>
        <select
          onChange={(e) => setFilter("recommendation", e.target.value)}
          className="rounded-md border border-slate-300 bg-transparent px-3 py-1.5 text-sm dark:border-slate-600"
        >
          <option value="">All recommendations</option>
          <option value="APPLY">Apply</option>
          <option value="REVIEW">Review</option>
          <option value="LOW_PRIORITY">Low priority</option>
          <option value="DO_NOT_APPLY">Do not apply</option>
        </select>
        <label className="flex items-center gap-1.5 text-sm text-slate-600 dark:text-slate-300">
          <input
            type="checkbox"
            onChange={(e) => setFilter("remote_only", e.target.checked ? "true" : "")}
          />
          Remote only
        </label>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500 dark:bg-slate-800">
            <tr>
              <th className="px-4 py-3">Job</th>
              <th className="px-4 py-3">Region</th>
              <th className="px-4 py-3">Eligibility</th>
              <th className="px-4 py-3">Score</th>
              <th className="px-4 py-3">Recommendation</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
            {jobs.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                  No jobs. Import one to get started.
                </td>
              </tr>
            ) : (
              jobs.map((j) => (
                <tr key={j.id} className="bg-white dark:bg-slate-900/40">
                  <td className="px-4 py-3">
                    <Link href={`/jobs/${j.id}`} className="font-medium hover:underline">
                      {j.title}
                    </Link>
                    <div className="text-xs text-slate-500">
                      {j.company}
                      {j.country ? ` · ${j.country}` : ""}
                      {j.remote ? " · Remote" : ""}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-slate-600 dark:text-slate-300">
                    {j.region ?? "—"}
                  </td>
                  <td className="px-4 py-3">
                    <EligibilityBadge value={j.eligibility} />
                  </td>
                  <td className="px-4 py-3">
                    <ScoreBadge value={j.match_score} />
                  </td>
                  <td className="px-4 py-3">
                    <RecommendationBadge value={j.recommendation} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        onClick={() => runAction(j.id, "analyze")}
                        disabled={busyId === j.id}
                        className="rounded border border-slate-300 px-2 py-1 text-xs hover:bg-slate-100 disabled:opacity-50 dark:border-slate-600 dark:hover:bg-slate-800"
                      >
                        {busyId === j.id ? "…" : j.analyzed ? "Re-analyze" : "Analyze"}
                      </button>
                      <button
                        onClick={() => runAction(j.id, "match")}
                        disabled={busyId === j.id || !j.analyzed}
                        title={j.analyzed ? "" : "Analyze first"}
                        className="rounded border border-slate-300 px-2 py-1 text-xs hover:bg-slate-100 disabled:opacity-50 dark:border-slate-600 dark:hover:bg-slate-800"
                      >
                        Match
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs text-slate-400">
        Analyze runs local Qwen3 on the job text; Match scores it against your profile
        (set skills on the Profile page first). Both may take a few seconds.
      </p>
    </main>
  );
}
