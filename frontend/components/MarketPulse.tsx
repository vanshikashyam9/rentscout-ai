"use client";

/**
 * Market snapshot on the landing page.
 *
 * Deliberately sourced from CMHC's Rental Market Survey rather than from the
 * rentals table: the listings on this site are seeded samples, so quoting an
 * "average asking rent" off them would present made-up numbers as market fact.
 * The vacancy data is real, so that is what the landing page leads with.
 */

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { ApiErrorShape, VacancyTrend } from "@/lib/types";

const AREA = "Vancouver CMA";

export default function MarketPulse() {
  const [trend, setTrend] = useState<VacancyTrend | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    api
      .get<VacancyTrend | ApiErrorShape>(
        `/market/trend?area=${encodeURIComponent(AREA)}`
      )
      .then((data) => {
        if ("error" in data) setError(true);
        else setTrend(data);
      })
      .catch(() => setError(true));
  }, []);

  if (error) {
    return (
      <div className="rounded-2xl border border-line bg-moss/60 p-6 text-sm text-ink-soft">
        Market data is unavailable. Start the backend to see CMHC figures here.
      </div>
    );
  }

  const series = trend?.series ?? [];
  const latest = series.at(-1);
  const first = series[0];
  const change =
    latest && first
      ? +(latest.vacancy_rate - first.vacancy_rate).toFixed(1)
      : null;

  return (
    <div className="rounded-2xl border border-line bg-white p-6 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-widest text-evergreen">
        Metro Vancouver right now
      </p>

      <dl className="mt-4 grid grid-cols-2 gap-6">
        <div>
          <dt className="text-sm text-ink-soft">
            Vacancy rate{latest ? `, ${latest.year}` : ""}
          </dt>
          <dd className="font-display text-3xl font-600 text-ink">
            {latest ? `${latest.vacancy_rate}%` : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-sm text-ink-soft">
            Change since {first?.year ?? "—"}
          </dt>
          <dd className="font-display text-3xl font-600 text-ink">
            {change === null ? "—" : `${change > 0 ? "+" : ""}${change}`}
          </dd>
        </div>
      </dl>

      <div className="mt-6 border-t border-line pt-4">
        <p className="text-sm text-ink-soft">
          {latest && latest.vacancy_rate < 2
            ? "A tight market — expect competition and move quickly."
            : "More supply than recent years — there is room to compare."}
        </p>
        <p className="mt-2 text-xs text-ink-soft">
          Source: CMHC Rental Market Survey
        </p>
      </div>
    </div>
  );
}
