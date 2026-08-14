"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { ApiErrorShape, VacancyTrend } from "@/lib/types";
import VacancyChart from "@/components/VacancyChart";

type Status = "loading" | "done" | "error";

const QUICK_AREAS = [
  "Vancouver CMA",
  "Downtown",
  "Burnaby",
  "Richmond",
  "Surrey",
  "New Westminster",
  "North Vancouver",
  "Langley",
];

/** What a vacancy rate actually means for someone trying to find a place. */
function readVacancy(rate: number) {
  if (rate < 1)
    return {
      label: "Extremely tight",
      note: "Expect competition, fast turnover, and little room to negotiate.",
    };
  if (rate < 2)
    return {
      label: "Tight",
      note: "Move quickly on listings you like; landlords hold the advantage.",
    };
  if (rate < 3)
    return {
      label: "Balanced",
      note: "Reasonable choice available. Some room to compare before deciding.",
    };
  return {
    label: "Renter-friendly",
    note: "More supply than usual — worth negotiating rent or move-in terms.",
  };
}

export default function MarketPage() {
  const [zones, setZones] = useState<string[]>([]);
  const [area, setArea] = useState("Vancouver CMA");
  const [trend, setTrend] = useState<VacancyTrend | null>(null);
  const [status, setStatus] = useState<Status>("loading");
  const [showTable, setShowTable] = useState(false);

  useEffect(() => {
    api
      .get<{ zones: string[] }>("/market/zones")
      .then((d) => setZones(d.zones))
      .catch(() => setZones([]));
  }, []);

  // State is only set in the async continuation, never synchronously in the
  // effect body. `ignore` drops responses from a superseded area.
  useEffect(() => {
    let ignore = false;

    (async () => {
      try {
        const data = await api.get<VacancyTrend | ApiErrorShape>(
          `/market/trend?area=${encodeURIComponent(area)}`
        );
        if (ignore) return;

        if ("error" in data) {
          setTrend(null);
          setStatus("error");
          return;
        }
        setTrend(data);
        setStatus("done");
      } catch {
        if (!ignore) {
          setTrend(null);
          setStatus("error");
        }
      }
    })();

    return () => {
      ignore = true;
    };
  }, [area]);

  // Showing the spinner belongs to the click, not the effect.
  function selectArea(next: string) {
    if (next === area) return;
    setStatus("loading");
    setArea(next);
  }

  const series = trend?.series ?? [];
  const latest = series.at(-1);
  const first = series[0];
  const change =
    latest && first ? +(latest.vacancy_rate - first.vacancy_rate).toFixed(2) : null;
  const reading = latest ? readVacancy(latest.vacancy_rate) : null;

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="font-display text-3xl font-700 text-ink">
        Metro Vancouver rental market
      </h1>
      <p className="mt-2 max-w-xl text-ink-soft">
        Vacancy rates from CMHC&apos;s annual Rental Market Survey. A lower rate
        means fewer empty units — and a harder search.
      </p>

      <div className="mt-8 flex flex-wrap items-center gap-2">
        {QUICK_AREAS.map((a) => (
          <button
            key={a}
            onClick={() => selectArea(a)}
            className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
              area === a
                ? "border-evergreen bg-evergreen text-paper"
                : "border-line text-ink-soft hover:border-evergreen hover:text-evergreen"
            }`}
          >
            {a}
          </button>
        ))}

        {zones.length > 0 && (
          <select
            value={zones.includes(area) ? area : ""}
            onChange={(e) => e.target.value && selectArea(e.target.value)}
            className="rounded-full border border-line bg-white px-4 py-1.5 text-sm text-ink-soft outline-none focus:border-evergreen"
          >
            <option value="">All CMHC zones…</option>
            {zones.map((z) => (
              <option key={z} value={z}>
                {z}
              </option>
            ))}
          </select>
        )}
      </div>

      {status === "error" && (
        <p className="mt-8 text-risk-high">
          No CMHC data for that area. Try one of the zones above.
        </p>
      )}

      {status === "loading" && (
        <p className="mt-8 text-ink-soft">Loading market data…</p>
      )}

      {status === "done" && latest && reading && (
        <>
          <div className="mt-8 grid gap-5 sm:grid-cols-3">
            <div className="rounded-2xl border border-line bg-white p-5">
              <p className="text-sm text-ink-soft">
                Vacancy rate, {latest.year}
              </p>
              <p className="mt-1 font-display text-4xl font-700 text-ink">
                {latest.vacancy_rate}%
              </p>
              <p className="mt-1 text-sm font-semibold text-evergreen">
                {reading.label}
              </p>
            </div>

            <div className="rounded-2xl border border-line bg-white p-5">
              <p className="text-sm text-ink-soft">
                Change since {first.year}
              </p>
              <p className="mt-1 font-display text-4xl font-700 text-ink">
                {change !== null && change > 0 ? "+" : ""}
                {change}
              </p>
              <p className="mt-1 text-sm text-ink-soft">
                percentage points
              </p>
            </div>

            <div className="rounded-2xl border border-line bg-white p-5">
              <p className="text-sm text-ink-soft">What this means</p>
              <p className="mt-1 text-sm text-ink">{reading.note}</p>
            </div>
          </div>

          <div className="mt-6 rounded-2xl border border-line bg-white p-6">
            <div className="mb-2 flex items-baseline justify-between gap-4">
              <h2 className="font-display text-lg font-600 text-ink">
                Vacancy rate in {trend?.area}
              </h2>
              <button
                onClick={() => setShowTable((v) => !v)}
                className="text-sm font-medium text-evergreen hover:text-evergreen-deep"
              >
                {showTable ? "Show chart" : "Show table"}
              </button>
            </div>

            {showTable ? (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-line text-left text-ink-soft">
                    <th className="py-2 font-medium">Year</th>
                    <th className="py-2 text-right font-medium">Vacancy rate</th>
                  </tr>
                </thead>
                <tbody>
                  {series.map((d) => (
                    <tr key={d.year} className="border-b border-line/60">
                      <td className="py-2 tabular-nums text-ink">{d.year}</td>
                      <td className="py-2 text-right tabular-nums text-ink">
                        {d.vacancy_rate}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <VacancyChart series={series} />
            )}

            {trend && trend.zones_matched.length > 1 && (
              <p className="mt-4 text-xs text-ink-soft">
                Averaged across {trend.zones_matched.length} CMHC zones:{" "}
                {trend.zones_matched.join(", ")}.
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
