"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { ScamAnalysis } from "@/lib/types";

type Status = "idle" | "loading" | "done" | "error";

const RISK_STYLES: Record<ScamAnalysis["risk_level"], string> = {
  LOW: "bg-moss text-evergreen-deep",
  MEDIUM: "bg-amber-50 text-risk-mid",
  HIGH: "bg-red-50 text-risk-high",
};

const RISK_COPY: Record<ScamAnalysis["risk_level"], string> = {
  LOW: "Nothing obvious flagged. Still verify in person before paying anything.",
  MEDIUM: "Some warning signs. Ask questions and confirm the unit exists.",
  HIGH: "Several strong warning signs. Treat this listing with real caution.",
};

const EXAMPLES = [
  {
    label: "Try a suspicious listing",
    title: "URGENT! Cash only, deposit first, available immediately — DM quickly",
    price: "900",
    location: "Downtown",
  },
  {
    label: "Try a normal listing",
    title: "Bright 1 bedroom apartment in Burnaby with in-suite laundry",
    price: "2100",
    location: "Burnaby",
  },
];

export default function AnalyzePage() {
  const [title, setTitle] = useState("");
  const [price, setPrice] = useState("");
  const [location, setLocation] = useState("");
  const [result, setResult] = useState<ScamAnalysis | null>(null);
  const [status, setStatus] = useState<Status>("idle");

  async function check(
    nextTitle = title,
    nextPrice = price,
    nextLocation = location
  ) {
    if (!nextTitle.trim()) return;
    setStatus("loading");
    try {
      const data = await api.post<ScamAnalysis>("/analyze-listing", {
        title: nextTitle,
        price: nextPrice,
        location: nextLocation.trim() || null,
      });
      setResult(data);
      setStatus("done");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="font-display text-3xl font-700 text-ink">
        Check a listing for scams
      </h1>
      <p className="mt-2 text-ink-soft">
        Paste the title and asking price from any rental ad. RentScout screens it
        for pressure tactics, payment red flags, and prices that are too good to
        be true.
      </p>

      <div className="mt-8 rounded-2xl border border-line bg-white p-6">
        <label className="block text-sm">
          <span className="mb-1 block font-medium text-ink">Listing title</span>
          <textarea
            rows={3}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Paste the listing headline here"
            className="w-full resize-y rounded-lg border border-line px-3 py-2 outline-none focus:border-evergreen"
          />
        </label>

        <div className="mt-4 flex flex-wrap gap-4">
          <label className="block text-sm">
            <span className="mb-1 block font-medium text-ink">
              Monthly rent asked
            </span>
            <input
              type="text"
              inputMode="numeric"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              placeholder="e.g. 1800"
              className="w-40 rounded-lg border border-line px-3 py-2 outline-none focus:border-evergreen"
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1 block font-medium text-ink">
              Area{" "}
              <span className="font-normal text-ink-soft">
                (optional, improves the price check)
              </span>
            </span>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Burnaby"
              className="w-52 rounded-lg border border-line px-3 py-2 outline-none focus:border-evergreen"
            />
          </label>
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            onClick={() => check()}
            disabled={!title.trim() || status === "loading"}
            className="rounded-full bg-evergreen px-6 py-2.5 text-sm font-semibold text-paper transition-colors hover:bg-evergreen-deep disabled:opacity-50"
          >
            {status === "loading" ? "Checking…" : "Check listing"}
          </button>

          {EXAMPLES.map((ex) => (
            <button
              key={ex.label}
              onClick={() => {
                setTitle(ex.title);
                setPrice(ex.price);
                setLocation(ex.location);
                check(ex.title, ex.price, ex.location);
              }}
              className="text-sm text-ink-soft underline decoration-line underline-offset-4 hover:text-evergreen"
            >
              {ex.label}
            </button>
          ))}
        </div>
      </div>

      {status === "error" && (
        <p className="mt-6 text-risk-high">
          Couldn&apos;t reach the server. Make sure the backend is running.
        </p>
      )}

      {status === "done" && result && (
        <div className="mt-6 rounded-2xl border border-line bg-white p-6">
          <div className="flex flex-wrap items-center gap-3">
            <span
              className={`rounded-full px-3 py-1 text-sm font-semibold ${
                RISK_STYLES[result.risk_level]
              }`}
            >
              {result.risk_level} risk
            </span>
            <span className="text-sm text-ink-soft tabular-nums">
              Risk score {result.risk_score}
            </span>
          </div>

          <p className="mt-3 text-sm text-ink">{RISK_COPY[result.risk_level]}</p>

          {result.reasons.length > 0 && (
            <>
              <h2 className="mt-5 text-sm font-semibold text-ink">
                What we flagged
              </h2>
              <ul className="mt-2 space-y-1.5">
                {result.reasons.map((r) => (
                  <li key={r} className="flex gap-2 text-sm text-ink-soft">
                    <span className="text-risk-mid">!</span>
                    {r}
                  </li>
                ))}
              </ul>
            </>
          )}

          <p className="mt-5 border-t border-line pt-4 text-xs text-ink-soft">
            This is an automated keyword and price screen, not a guarantee. A
            listing can pass every check and still be fraudulent. Never send a
            deposit or e-transfer before viewing a unit in person and confirming
            who owns it.
          </p>
        </div>
      )}
    </div>
  );
}
