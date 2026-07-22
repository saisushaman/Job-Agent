import Link from "next/link";

import HealthStatus from "@/components/HealthStatus";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/jobs", label: "Jobs" },
  { href: "/resumes", label: "Resumes" },
  { href: "/profile", label: "Profile" },
];

export default function Nav() {
  return (
    <header className="mb-8 flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-4 dark:border-slate-700">
      <div className="flex flex-wrap items-center gap-1">
        <Link href="/" className="mr-3 text-lg font-bold tracking-tight">
          Job-Agent
        </Link>
        {LINKS.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className="rounded-md px-3 py-1.5 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
          >
            {l.label}
          </Link>
        ))}
      </div>
      <HealthStatus />
    </header>
  );
}
