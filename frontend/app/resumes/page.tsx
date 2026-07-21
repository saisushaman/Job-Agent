"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import {
  getResume,
  getResumeVersion,
  listResumes,
  resumeVersionDownloadUrl,
  uploadResumeVersion,
  type ResumeDetail,
  type ResumeSummary,
  type ResumeVersionDetail,
} from "@/lib/api";

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ResumesPage() {
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ResumeDetail | null>(null);
  const [preview, setPreview] = useState<ResumeVersionDetail | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const refreshList = useCallback(async () => {
    const list = await listResumes();
    setResumes(list);
    setSelectedId((cur) => cur ?? (list[0]?.id ?? null));
  }, []);

  useEffect(() => {
    refreshList().catch((e) => setError(String(e.message ?? e)));
  }, [refreshList]);

  useEffect(() => {
    if (selectedId == null) return;
    setPreview(null);
    getResume(selectedId)
      .then(setDetail)
      .catch((e) => setError(String(e.message ?? e)));
  }, [selectedId]);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const file = fileRef.current?.files?.[0];
    if (!file || selectedId == null) return;
    setUploading(true);
    try {
      await uploadResumeVersion(selectedId, file);
      if (fileRef.current) fileRef.current.value = "";
      await Promise.all([
        refreshList(),
        getResume(selectedId).then(setDetail),
      ]);
    } catch (err) {
      setError(String((err as Error).message ?? err));
    } finally {
      setUploading(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-6">
        <Link
          href="/"
          className="text-sm text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
        >
          ← Dashboard
        </Link>
        <h1 className="mt-2 text-3xl font-bold tracking-tight">Resumes</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Upload PDF, DOCX, or TXT resumes for each track. Each upload is kept as a new
          version.
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-[260px_1fr]">
        {/* Track list */}
        <aside className="space-y-2">
          {resumes.map((r) => (
            <button
              key={r.id}
              onClick={() => setSelectedId(r.id)}
              className={`w-full rounded-lg border px-4 py-3 text-left transition ${
                r.id === selectedId
                  ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-950/40"
                  : "border-slate-200 bg-white hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800"
              }`}
            >
              <div className="font-medium">{r.name}</div>
              <div className="text-xs text-slate-500 dark:text-slate-400">
                {r.version_count === 0
                  ? "No versions yet"
                  : `${r.version_count} version${r.version_count > 1 ? "s" : ""} · latest v${r.latest_version_number}`}
              </div>
            </button>
          ))}
        </aside>

        {/* Detail */}
        <section className="space-y-6">
          {detail && (
            <>
              <form
                onSubmit={handleUpload}
                className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800"
              >
                <h2 className="mb-3 text-lg font-semibold">{detail.name}</h2>
                <div className="flex flex-wrap items-center gap-3">
                  <input
                    ref={fileRef}
                    type="file"
                    accept=".pdf,.docx,.txt"
                    required
                    className="text-sm text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-indigo-600 file:px-3 file:py-2 file:text-white hover:file:bg-indigo-700 dark:text-slate-300"
                  />
                  <button
                    type="submit"
                    disabled={uploading}
                    className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-white dark:text-slate-900"
                  >
                    {uploading ? "Uploading…" : "Upload version"}
                  </button>
                </div>
              </form>

              <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
                  Version history
                </h3>
                {detail.versions.length === 0 ? (
                  <p className="text-sm text-slate-500">No versions uploaded yet.</p>
                ) : (
                  <ul className="divide-y divide-slate-100 dark:divide-slate-700">
                    {[...detail.versions].reverse().map((v) => (
                      <li
                        key={v.id}
                        className="flex flex-wrap items-center justify-between gap-2 py-3"
                      >
                        <div>
                          <span className="font-medium">v{v.version_number}</span>{" "}
                          <span className="text-sm text-slate-600 dark:text-slate-300">
                            {v.original_filename}
                          </span>
                          <div className="text-xs text-slate-400">
                            {formatBytes(v.file_size)} ·{" "}
                            {new Date(v.created_at).toLocaleString()}
                          </div>
                        </div>
                        <div className="flex gap-3 text-sm">
                          <button
                            onClick={() =>
                              getResumeVersion(v.id).then(setPreview).catch((e) =>
                                setError(String(e.message ?? e)),
                              )
                            }
                            className="text-indigo-600 hover:underline"
                          >
                            Preview
                          </button>
                          <a
                            href={resumeVersionDownloadUrl(v.id)}
                            className="text-slate-500 hover:underline"
                          >
                            Download
                          </a>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {preview && (
                <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
                  <div className="mb-2 flex items-center justify-between">
                    <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                      Preview · v{preview.version_number} ·{" "}
                      {preview.original_filename}
                    </h3>
                    <button
                      onClick={() => setPreview(null)}
                      className="text-xs text-slate-400 hover:text-slate-600"
                    >
                      Close
                    </button>
                  </div>
                  <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-md bg-slate-50 p-3 text-sm text-slate-700 dark:bg-slate-900 dark:text-slate-300">
                    {preview.parsed_text || "(no text extracted)"}
                  </pre>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </main>
  );
}
