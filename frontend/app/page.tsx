"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import Nav from "@/components/Nav";
import { RecommendationBadge, ScoreBadge } from "@/components/badges";
import { fetchStats, type DashboardStats } from "@/lib/api";

function StatCard({ label, value, accent }: { label: string; value: number; accent?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</div>
      <div className={`mt-2 text-3xl font-semibold ${accent ?? ""}`}>{value}</div>
    </div>
  );
}

function Breakdown({ title, data }: { title: string; data: Record<string, number> }) {
  const entries = Object.entries(data).filter(([, v]) => v > 0);
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
        {title}
      </h3>
      {entries.length === 0 ? (
        <p className="text-sm text-slate-400">No data yet.</p>
      ) : (
        <ul className="space-y-1.5 text-sm">
          {entries.map(([k, v]) => (
            <li key={k} className="flex justify-between">
              <span className="text-slate-600 dark:text-slate-300">{k.replace(/_/g, " ")}</span>
              <span className="font-semibold">{v}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats()
      .then(setStats)
      .catch((e) => setError(String(e.message ?? e)));
  }, []);

  const p = stats?.pipeline ?? {};

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <Nav />

      {error && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      <h1 className="mb-1 text-2xl font-bold tracking-tight">Dashboard</h1>
      <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">
        Local-first AI job search &amp; application management
      </p>

      <section className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-7">
        <StatCard label="Total Jobs" value={stats?.total_jobs ?? 0} />
        <StatCard label="Review" value={p.REVIEW ?? 0} accent="text-amber-600" />
        <StatCard label="Approved" value={p.APPROVED ?? 0} accent="text-blue-600" />
        <StatCard label="Applied" value={p.APPLIED ?? 0} accent="text-indigo-600" />
        <StatCard label="Interview" value={p.INTERVIEW ?? 0} accent="text-purple-600" />
        <StatCard label="Offers" value={p.OFFER ?? 0} accent="text-emerald-600" />
        <StatCard label="Rejected" value={p.REJECTED ?? 0} accent="text-red-600" />
      </section>

      <section className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Breakdown title="Region" data={stats?.regions ?? {}} />
        <Breakdown title="Eligibility" data={stats?.eligibility ?? {}} />
        <Breakdown title="USA sponsorship" data={stats?.sponsorship_us ?? {}} />
        <Breakdown title="Recommendations" data={stats?.recommendations ?? {}} />
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Top matching jobs
          </h3>
          <Link href="/jobs" className="text-sm text-indigo-600 hover:underline">
            View all jobs →
          </Link>
        </div>
        {!stats || stats.top_matches.length === 0 ? (
          <p className="text-sm text-slate-400">
            No matches yet. Import a job on the Jobs page, then analyze and match it.
          </p>
        ) : (
          <ul className="divide-y divide-slate-100 dark:divide-slate-700">
            {stats.top_matches.map((m) => (
              <li key={m.job_id} className="flex items-center justify-between gap-3 py-3">
                <Link href={`/jobs/${m.job_id}`} className="min-w-0">
                  <div className="truncate font-medium hover:underline">{m.title}</div>
                  <div className="truncate text-sm text-slate-500">
                    {m.company} · {m.region ?? "—"}
                  </div>
                </Link>
                <div className="flex items-center gap-2">
                  <ScoreBadge value={m.overall_score} />
                  <RecommendationBadge value={m.recommendation} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
