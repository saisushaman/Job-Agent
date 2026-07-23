"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import Nav from "@/components/Nav";
import {
  approveTailored,
  generateTailored,
  getApplication,
  getTailored,
  tailorDocumentUrl,
  type ApplicationDetail,
  type TailoredDocument,
} from "@/lib/api";

export default function TailorPage() {
  const params = useParams();
  const id = Number(params.id);
  const [appInfo, setAppInfo] = useState<ApplicationDetail | null>(null);
  const [doc, setDoc] = useState<TailoredDocument | null>(null);
  const [questions, setQuestions] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  useEffect(() => {
    getApplication(id).then(setAppInfo).catch(() => {});
    getTailored(id)
      .then(setDoc)
      .catch((e) => setError(String(e.message ?? e)));
  }, [id]);

  async function generate() {
    setError(null);
    setBusy("gen");
    try {
      const qs = questions
        .split("\n")
        .map((q) => q.trim())
        .filter(Boolean);
      setDoc(await generateTailored(id, qs.length ? { questions: qs } : {}));
    } catch (e) {
      setError(String((e as Error).message ?? e));
    } finally {
      setBusy(null);
    }
  }

  async function approve() {
    setError(null);
    setBusy("approve");
    try {
      setDoc(await approveTailored(id));
    } catch (e) {
      setError(String((e as Error).message ?? e));
    } finally {
      setBusy(null);
    }
  }

  const box =
    "max-h-96 overflow-auto whitespace-pre-wrap rounded-md border border-slate-200 bg-slate-50 p-3 text-sm dark:border-slate-700 dark:bg-slate-900";

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <Nav />
      <Link href={`/applications/${id}`} className="text-sm text-slate-500 hover:underline">
        ← Application
      </Link>

      <div className="mb-4 mt-2 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Tailor application</h1>
          {appInfo && (
            <p className="text-slate-500">
              {appInfo.job_title} · {appInfo.job_company}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={generate}
            disabled={busy !== null}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100 disabled:opacity-50 dark:border-slate-600 dark:hover:bg-slate-800"
          >
            {busy === "gen" ? "Generating…" : doc ? "Regenerate" : "Generate"}
          </button>
          {doc && doc.status === "DRAFT" && (
            <button
              onClick={approve}
              disabled={busy !== null}
              className="rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-50 dark:bg-white dark:text-slate-900"
            >
              {busy === "approve" ? "Approving…" : "Approve"}
            </button>
          )}
        </div>
      </div>

      <p className="mb-4 text-xs text-slate-400">
        The AI only reorders and re-emphasizes facts already in your resume/profile — it
        never invents experience, skills, or achievements. Review the before/after, then
        approve to save.
      </p>

      {error && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      {!doc && (
        <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
          <label className="mb-1 block text-sm font-medium">
            Application questions (optional, one per line)
          </label>
          <textarea
            value={questions}
            onChange={(e) => setQuestions(e.target.value)}
            placeholder="Why do you want to work here?"
            className="min-h-24 w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm dark:border-slate-600"
          />
          <p className="mt-2 text-xs text-slate-400">
            Click Generate to draft a tailored resume, cover letter, and answers.
          </p>
        </div>
      )}

      {doc && (
        <div className="space-y-6">
          <div className="flex items-center gap-2 text-sm">
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                doc.status === "APPROVED"
                  ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300"
                  : "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300"
              }`}
            >
              {doc.status}
            </span>
            <span className="text-slate-400">
              Downloads:{" "}
              {(["txt", "docx"] as const).map((f) => (
                <a
                  key={f}
                  href={tailorDocumentUrl(id, "resume", f)}
                  className="mx-1 text-indigo-600 hover:underline"
                >
                  resume.{f}
                </a>
              ))}
              {(["txt", "docx"] as const).map((f) => (
                <a
                  key={f}
                  href={tailorDocumentUrl(id, "cover_letter", f)}
                  className="mx-1 text-indigo-600 hover:underline"
                >
                  cover.{f}
                </a>
              ))}
            </span>
          </div>

          {/* before / after */}
          <div className="grid gap-4 lg:grid-cols-2">
            <div>
              <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
                Before (original)
              </h3>
              <div className={box}>{doc.before_resume || "(none)"}</div>
            </div>
            <div>
              <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
                After (tailored)
              </h3>
              <div className={box}>{doc.tailored_resume}</div>
            </div>
          </div>

          {doc.changes_summary.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
              <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
                What changed
              </h3>
              <ul className="list-disc pl-5 text-sm text-slate-600 dark:text-slate-300">
                {doc.changes_summary.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          <div>
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Cover letter
            </h3>
            <div className={box}>{doc.cover_letter}</div>
          </div>

          {doc.draft_answers.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
              <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
                Draft answers
              </h3>
              <div className="space-y-3">
                {doc.draft_answers.map((qa, i) => (
                  <div key={i}>
                    <div className="text-sm font-medium">{qa.question}</div>
                    <div className="text-sm text-slate-600 dark:text-slate-300">
                      {qa.answer}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </main>
  );
}
