import type { ReactNode } from "react";

function Pill({ children, className }: { children: ReactNode; className: string }) {
  return (
    <span
      className={`inline-block rounded-full px-2 py-0.5 text-xs font-semibold ${className}`}
    >
      {children}
    </span>
  );
}

export function RecommendationBadge({ value }: { value: string | null }) {
  if (!value) return <span className="text-xs text-slate-400">—</span>;
  const map: Record<string, string> = {
    APPLY: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300",
    REVIEW: "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300",
    LOW_PRIORITY: "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300",
    DO_NOT_APPLY: "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300",
  };
  return <Pill className={map[value] ?? map.LOW_PRIORITY}>{value.replace(/_/g, " ")}</Pill>;
}

export function EligibilityBadge({ value }: { value: string | null }) {
  if (!value) return <span className="text-xs text-slate-400">—</span>;
  const map: Record<string, string> = {
    ELIGIBLE: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300",
    REVIEW: "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300",
    NOT_ELIGIBLE: "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300",
  };
  return <Pill className={map[value] ?? map.REVIEW}>{value.replace(/_/g, " ")}</Pill>;
}

export function ScoreBadge({ value }: { value: number | null }) {
  if (value == null) return <span className="text-xs text-slate-400">—</span>;
  const cls =
    value >= 75
      ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300"
      : value >= 55
        ? "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300"
        : "bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-300";
  return <Pill className={cls}>{value.toFixed(0)}</Pill>;
}
