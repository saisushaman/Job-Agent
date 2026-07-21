import HealthStatus from "@/components/HealthStatus";

const STATS: { label: string; value: number; accent: string }[] = [
  { label: "Total Jobs", value: 0, accent: "text-slate-900 dark:text-white" },
  { label: "Review", value: 0, accent: "text-amber-600" },
  { label: "Approved", value: 0, accent: "text-blue-600" },
  { label: "Applied", value: 0, accent: "text-indigo-600" },
  { label: "Interview", value: 0, accent: "text-purple-600" },
  { label: "Offers", value: 0, accent: "text-emerald-600" },
  { label: "Rejected", value: 0, accent: "text-red-600" },
];

export default function DashboardPage() {
  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Job-Agent</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Local-first AI job search &amp; application management
          </p>
        </div>
        <HealthStatus />
      </header>

      <section
        aria-label="Pipeline statistics"
        className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4"
      >
        {STATS.map((s) => (
          <div
            key={s.label}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
          >
            <div className="text-sm font-medium text-slate-500 dark:text-slate-400">
              {s.label}
            </div>
            <div className={`mt-2 text-3xl font-semibold ${s.accent}`}>
              {s.value}
            </div>
          </div>
        ))}
      </section>

      <section className="mt-10 rounded-xl border border-dashed border-slate-300 bg-white/50 p-6 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-800/40 dark:text-slate-400">
        <h2 className="mb-1 text-base font-semibold text-slate-700 dark:text-slate-200">
          Phase 1 — Foundation
        </h2>
        <p>
          The scaffold is live and the dashboard is talking to the backend (see the
          status badge above). Job import, AI analysis, matching, applications, email,
          and automation arrive in later phases — see{" "}
          <code className="rounded bg-slate-100 px-1 py-0.5 dark:bg-slate-700">
            PROJECT_SPEC.md
          </code>
          .
        </p>
      </section>
    </main>
  );
}
