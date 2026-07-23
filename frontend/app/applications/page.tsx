"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import Nav from "@/components/Nav";
import { ScoreBadge } from "@/components/badges";
import {
  APPLICATION_STATUSES,
  listApplications,
  updateApplication,
  type ApplicationCard,
} from "@/lib/api";

const COLUMN_LABEL: Record<string, string> = {
  DISCOVERED: "Discovered",
  REVIEW: "Review",
  APPROVED: "Approved",
  APPLICATION_READY: "Ready",
  APPLYING: "Applying",
  APPLIED: "Applied",
  RESPONSE_RECEIVED: "Response",
  INTERVIEW: "Interview",
  OFFER: "Offer",
  REJECTED: "Rejected",
  ON_HOLD: "On hold",
  NOT_ELIGIBLE: "Not eligible",
};

export default function ApplicationsPage() {
  const [cards, setCards] = useState<ApplicationCard[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [dragId, setDragId] = useState<number | null>(null);

  const refresh = useCallback(() => {
    listApplications()
      .then(setCards)
      .catch((e) => setError(String(e.message ?? e)));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function moveTo(id: number, status: string) {
    const card = cards.find((c) => c.id === id);
    if (!card || card.status === status) return;
    // optimistic update
    setCards((cs) => cs.map((c) => (c.id === id ? { ...c, status } : c)));
    setError(null);
    try {
      await updateApplication(id, { status });
    } catch (e) {
      setError(String((e as Error).message ?? e));
      refresh(); // revert on failure
    }
  }

  return (
    <main className="mx-auto max-w-[1400px] px-6 py-10">
      <Nav />
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Applications</h1>
        <Link href="/jobs" className="text-sm text-indigo-600 hover:underline">
          Add jobs from Jobs →
        </Link>
      </div>
      <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">
        Drag cards between columns to update status. NOT_ELIGIBLE jobs can’t be moved into
        the apply columns.
      </p>

      {error && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="flex gap-3 overflow-x-auto pb-4">
        {APPLICATION_STATUSES.map((status) => {
          const items = cards.filter((c) => c.status === status);
          return (
            <div
              key={status}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => dragId != null && moveTo(dragId, status)}
              className="flex w-64 shrink-0 flex-col rounded-xl border border-slate-200 bg-slate-50 p-2 dark:border-slate-700 dark:bg-slate-900/40"
            >
              <div className="mb-2 flex items-center justify-between px-1">
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {COLUMN_LABEL[status] ?? status}
                </span>
                <span className="rounded-full bg-slate-200 px-2 text-xs text-slate-600 dark:bg-slate-700 dark:text-slate-300">
                  {items.length}
                </span>
              </div>
              <div className="flex flex-col gap-2">
                {items.map((c) => (
                  <div
                    key={c.id}
                    draggable
                    onDragStart={() => setDragId(c.id)}
                    onDragEnd={() => setDragId(null)}
                    className="cursor-grab rounded-lg border border-slate-200 bg-white p-3 shadow-sm active:cursor-grabbing dark:border-slate-700 dark:bg-slate-800"
                  >
                    <Link
                      href={`/applications/${c.id}`}
                      className="text-sm font-medium hover:underline"
                    >
                      {c.job_title}
                    </Link>
                    <div className="truncate text-xs text-slate-500">{c.job_company}</div>
                    <div className="mt-2 flex items-center gap-2">
                      <ScoreBadge value={c.match_score} />
                      {c.recommendation && (
                        <span className="text-[10px] uppercase text-slate-400">
                          {c.recommendation.replace(/_/g, " ")}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </main>
  );
}
