"use client";

import { useEffect, useState } from "react";

import { fetchHealth, type HealthResponse } from "@/lib/api";

type State =
  | { kind: "loading" }
  | { kind: "ok"; data: HealthResponse }
  | { kind: "error"; message: string };

export default function HealthStatus() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let active = true;
    fetchHealth()
      .then((data) => active && setState({ kind: "ok", data }))
      .catch(
        (err) =>
          active &&
          setState({ kind: "error", message: String(err?.message ?? err) }),
      );
    return () => {
      active = false;
    };
  }, []);

  const dot =
    state.kind === "ok"
      ? "bg-emerald-500"
      : state.kind === "error"
        ? "bg-red-500"
        : "bg-amber-400 animate-pulse";

  const label =
    state.kind === "ok"
      ? `Backend connected · v${state.data.version} · db ${state.data.database}`
      : state.kind === "error"
        ? "Backend unreachable"
        : "Checking backend…";

  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/70 px-3 py-1 text-sm text-slate-600 shadow-sm dark:border-slate-700 dark:bg-slate-800/60 dark:text-slate-300">
      <span className={`h-2.5 w-2.5 rounded-full ${dot}`} />
      <span>{label}</span>
    </div>
  );
}
