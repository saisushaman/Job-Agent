"use client";

import { useEffect, useState } from "react";

import Nav from "@/components/Nav";
import { getProfile, updateProfile, type Profile } from "@/lib/api";

const REGIONS = ["USA", "EUROPE", "OTHER"];

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [skills, setSkills] = useState("");
  const [languages, setLanguages] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getProfile()
      .then((p) => {
        setProfile(p);
        setSkills((p.skills ?? []).join(", "));
        setLanguages((p.languages ?? []).join(", "));
      })
      .catch((e) => setError(String(e.message ?? e)));
  }, []);

  function set<K extends keyof Profile>(key: K, value: Profile[K]) {
    setProfile((p) => (p ? { ...p, [key]: value } : p));
    setSaved(false);
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!profile) return;
    setError(null);
    setSaving(true);
    try {
      const updated = await updateProfile({
        full_name: profile.full_name,
        headline: profile.headline,
        years_experience: profile.years_experience,
        current_location: profile.current_location,
        current_country: profile.current_country,
        preferred_regions: profile.preferred_regions,
        needs_sponsorship: profile.needs_sponsorship,
        open_to_relocation: profile.open_to_relocation,
        open_to_remote: profile.open_to_remote,
        skills: skills.split(",").map((s) => s.trim()).filter(Boolean),
        languages: languages.split(",").map((s) => s.trim()).filter(Boolean),
      });
      setProfile(updated);
      setSaved(true);
    } catch (err) {
      setError(String((err as Error).message ?? err));
    } finally {
      setSaving(false);
    }
  }

  const input =
    "w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm dark:border-slate-600";
  const label = "mb-1 block text-sm font-medium text-slate-600 dark:text-slate-300";

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Nav />
      <h1 className="mb-1 text-2xl font-bold tracking-tight">Candidate profile</h1>
      <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">
        Used to match jobs. Facts here are yours — the AI never invents profile content.
      </p>

      {error && (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      {profile && (
        <form
          onSubmit={handleSave}
          className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800"
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className={label}>Full name</label>
              <input
                className={input}
                value={profile.full_name ?? ""}
                onChange={(e) => set("full_name", e.target.value)}
              />
            </div>
            <div>
              <label className={label}>Headline</label>
              <input
                className={input}
                value={profile.headline ?? ""}
                onChange={(e) => set("headline", e.target.value)}
              />
            </div>
            <div>
              <label className={label}>Years of experience</label>
              <input
                type="number"
                step="0.5"
                className={input}
                value={profile.years_experience ?? ""}
                onChange={(e) =>
                  set(
                    "years_experience",
                    e.target.value === "" ? null : Number(e.target.value),
                  )
                }
              />
            </div>
            <div>
              <label className={label}>Current location</label>
              <input
                className={input}
                value={profile.current_location ?? ""}
                onChange={(e) => set("current_location", e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className={label}>Skills (comma-separated)</label>
            <input
              className={input}
              value={skills}
              onChange={(e) => {
                setSkills(e.target.value);
                setSaved(false);
              }}
              placeholder="Python, FastAPI, PyTorch"
            />
          </div>
          <div>
            <label className={label}>Languages (comma-separated)</label>
            <input
              className={input}
              value={languages}
              onChange={(e) => {
                setLanguages(e.target.value);
                setSaved(false);
              }}
              placeholder="English"
            />
          </div>

          <div>
            <span className={label}>Preferred regions</span>
            <div className="flex gap-4">
              {REGIONS.map((r) => (
                <label key={r} className="flex items-center gap-1.5 text-sm">
                  <input
                    type="checkbox"
                    checked={profile.preferred_regions.includes(r)}
                    onChange={(e) =>
                      set(
                        "preferred_regions",
                        e.target.checked
                          ? [...profile.preferred_regions, r]
                          : profile.preferred_regions.filter((x) => x !== r),
                      )
                    }
                  />
                  {r}
                </label>
              ))}
            </div>
          </div>

          <div className="flex flex-wrap gap-6">
            {(
              [
                ["needs_sponsorship", "Needs sponsorship"],
                ["open_to_relocation", "Open to relocation"],
                ["open_to_remote", "Open to remote"],
              ] as const
            ).map(([key, text]) => (
              <label key={key} className="flex items-center gap-1.5 text-sm">
                <input
                  type="checkbox"
                  checked={profile[key]}
                  onChange={(e) => set(key, e.target.checked)}
                />
                {text}
              </label>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={saving}
              className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-white dark:text-slate-900"
            >
              {saving ? "Saving…" : "Save profile"}
            </button>
            {saved && <span className="text-sm text-emerald-600">Saved ✓</span>}
          </div>
        </form>
      )}
    </main>
  );
}
