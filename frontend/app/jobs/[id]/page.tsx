"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import Nav from "@/components/Nav";
import {
  EligibilityBadge,
  RecommendationBadge,
  ScoreBadge,
} from "@/components/badges";
import { analyzeJob, getJobDetail, matchJob, type JobDetail } from "@/lib/api";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
        {title}
      </h2>
      {children}
    </div>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 py-1 text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="text-right font-medium">{value ?? "—"}</span>
    </div>
  );
}

export default function JobDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const [detail, setDetail] = useState<JobDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(() => {
    getJobDetail(id)
      .then(setDetail)
      .catch((e) => setError(String(e.message ?? e)));
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function run(action: "analyze" | "match") {
    setError(null);
    setBusy(action);
    try {
      if (action === "analyze") await analyzeJob(id);
      else await matchJob(id);
      load();
    } catch (e) {
      setError(String((e as Error).message ?? e));
    } finally {
      setBusy(null);
    }
  }

  const a = detail?.analysis?.result;
  const m = detail?.match?.result;

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <Nav />
      <Link href="/jobs" className="text-sm text-slate-500 hover:underline">
        ← All jobs
      </Link>

      {error && (
        <div className="my-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      {detail && (
        <>
          <div className="mb-6 mt-2 flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">{detail.job.title}</h1>
              <p className="text-slate-500">
                {detail.job.company}
                {detail.job.city ? ` · ${detail.job.city}` : ""}
                {detail.job.country ? `, ${detail.job.country}` : ""}
              </p>
              {detail.job.url && (
                <a
                  href={detail.job.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm text-indigo-600 hover:underline"
                >
                  Original posting ↗
                </a>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => run("analyze")}
                disabled={busy !== null}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100 disabled:opacity-50 dark:border-slate-600 dark:hover:bg-slate-800"
              >
                {busy === "analyze" ? "Analyzing…" : a ? "Re-analyze" : "Analyze"}
              </button>
              <button
                onClick={() => run("match")}
                disabled={busy !== null || !a}
                title={a ? "" : "Analyze first"}
                className="rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-50 dark:bg-white dark:text-slate-900"
              >
                {busy === "match" ? "Matching…" : "Match"}
              </button>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Analysis */}
            <Section title="Analysis">
              {!a ? (
                <p className="text-sm text-slate-400">Not analyzed yet.</p>
              ) : (
                <div>
                  <div className="mb-2 flex items-center gap-2">
                    <EligibilityBadge value={a.eligibility} />
                    {a.citizenship_required && (
                      <span className="text-xs font-semibold text-red-600">
                        Citizenship required
                      </span>
                    )}
                  </div>
                  <Row label="Region" value={a.region} />
                  <Row label="US sponsorship" value={a.sponsorship_us} />
                  <Row label="EU visa support" value={a.visa_support_eu} />
                  <Row label="Work auth required" value={String(a.work_authorization_required)} />
                  <Row label="Relocation" value={a.relocation} />
                  <Row label="English" value={a.english_compatibility} />
                  <Row label="Experience (min yrs)" value={a.experience_years_min} />
                  <Row
                    label="Salary"
                    value={
                      a.salary_min || a.salary_max
                        ? `${a.salary_min ?? "?"}–${a.salary_max ?? "?"} ${a.salary_currency ?? ""} ${a.salary_period ? `/ ${a.salary_period}` : ""}`
                        : "—"
                    }
                  />
                  {a.technical_skills.length > 0 && (
                    <div className="mt-3">
                      <div className="mb-1 text-xs uppercase text-slate-400">Skills</div>
                      <div className="flex flex-wrap gap-1.5">
                        {a.technical_skills.map((s) => (
                          <span
                            key={s}
                            className="rounded bg-slate-100 px-2 py-0.5 text-xs dark:bg-slate-700"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {a.citizenship_evidence && (
                    <p className="mt-3 text-xs italic text-slate-500">
                      Evidence: “{a.citizenship_evidence}”
                    </p>
                  )}
                  {a.concerns.length > 0 && (
                    <ul className="mt-3 list-disc pl-5 text-xs text-red-600">
                      {a.concerns.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  )}
                  {a.summary && (
                    <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">
                      {a.summary}
                    </p>
                  )}
                </div>
              )}
            </Section>

            {/* Match */}
            <Section title="Match">
              {!m ? (
                <p className="text-sm text-slate-400">
                  Not matched yet. {a ? "" : "Analyze first, then match."}
                </p>
              ) : (
                <div>
                  <div className="mb-3 flex items-center gap-2">
                    <ScoreBadge value={m.overall_score} />
                    <RecommendationBadge value={m.recommendation} />
                  </div>
                  {Object.entries(m.scores).map(([k, v]) => (
                    <Row key={k} label={k[0].toUpperCase() + k.slice(1)} value={v} />
                  ))}
                  {m.matched_skills.length > 0 && (
                    <p className="mt-3 text-sm">
                      <span className="text-emerald-600">Matched:</span>{" "}
                      {m.matched_skills.join(", ")}
                    </p>
                  )}
                  {m.missing_skills.length > 0 && (
                    <p className="text-sm">
                      <span className="text-red-600">Missing:</span>{" "}
                      {m.missing_skills.join(", ")}
                    </p>
                  )}
                  {m.reasoning && (
                    <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">
                      {m.reasoning}
                    </p>
                  )}
                </div>
              )}
            </Section>
          </div>

          {detail.job.description && (
            <div className="mt-6">
              <Section title="Description">
                <pre className="max-h-96 overflow-auto whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300">
                  {detail.job.description}
                </pre>
              </Section>
            </div>
          )}
        </>
      )}
    </main>
  );
}
