"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { RecommendationsResponse, Recommendation } from "@/lib/types";
import RentalCard from "@/components/RentalCard";

type Status = "idle" | "loading" | "done" | "error";

export default function SearchPage() {
  const [location, setLocation] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [results, setResults] = useState<Recommendation[]>([]);
  const [status, setStatus] = useState<Status>("idle");

  const search = useCallback(async () => {
    if (!maxPrice) return;
    setStatus("loading");
    try {
      const params = new URLSearchParams({ max_price: maxPrice });
      if (location.trim()) params.set("location", location.trim());
      const data = await api.get<RecommendationsResponse>(
        `/recommendations?${params.toString()}`
      );
      setResults(data.recommendations);
      setStatus("done");
    } catch {
      setStatus("error");
    }
  }, [location, maxPrice]);

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="font-display text-3xl font-700 text-ink">Find rentals</h1>
      <p className="mt-2 text-ink-soft">
        Enter your budget and area. Listings are ranked by affordability, with
        the reasons behind each match.
      </p>

      <div className="mt-6 rounded-xl border border-line bg-moss/50 p-4 text-sm text-ink-soft">
        <span className="font-semibold text-ink">
          These are sample listings.
        </span>{" "}
        They show how RentScout ranks and scores a search — the ranking is real,
        the units are not. To check a real listing you found somewhere else, use{" "}
        <Link
          href="/analyze"
          className="font-medium text-evergreen underline underline-offset-2"
        >
          Scam check
        </Link>
        .
      </div>

      <div className="mt-8 flex flex-wrap items-end gap-4 rounded-2xl border border-line bg-white p-5">
        <label className="flex-1 min-w-[180px] text-sm">
          <span className="mb-1 block font-medium text-ink">Area</span>
          <input
            type="text"
            placeholder="e.g. Burnaby, Surrey"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full rounded-lg border border-line px-3 py-2 outline-none focus:border-evergreen"
          />
        </label>

        <label className="flex-1 min-w-[180px] text-sm">
          <span className="mb-1 block font-medium text-ink">
            Maximum rent (monthly)
          </span>
          <input
            type="number"
            placeholder="e.g. 2500"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            className="w-full rounded-lg border border-line px-3 py-2 outline-none focus:border-evergreen"
          />
        </label>

        <button
          onClick={search}
          disabled={!maxPrice || status === "loading"}
          className="rounded-full bg-evergreen px-6 py-2.5 text-sm font-semibold text-paper transition-colors hover:bg-evergreen-deep disabled:opacity-50"
        >
          {status === "loading" ? "Searching…" : "Search"}
        </button>
      </div>

      <div className="mt-8">
        {status === "idle" && (
          <p className="text-ink-soft">
            Set a maximum rent to see ranked listings.
          </p>
        )}
        {status === "error" && (
          <p className="text-risk-high">
            Couldn&apos;t reach the server. Make sure the backend is running.
          </p>
        )}
        {status === "done" && results.length === 0 && (
          <p className="text-ink-soft">
            No listings under that budget yet. Try raising the maximum or
            widening the area.
          </p>
        )}
        {status === "done" && results.length > 0 && (
          <>
            <p className="mb-4 text-sm text-ink-soft">
              {results.length} listing{results.length === 1 ? "" : "s"} ranked
              by match
            </p>
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {results.map((r) => (
                <RentalCard
                  key={r.id}
                  rental={r}
                  score={r.score}
                  reasons={r.reasons}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
