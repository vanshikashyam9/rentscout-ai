"use client";

/**
 * Live market snapshot on the landing page.
 * Proof that the frontend talks to the FastAPI backend: these numbers
 * come from the rentals table, not from hardcoded copy.
 */

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { RentalListResponse } from "@/lib/types";

interface Pulse {
  listings: number;
  averageRent: number;
  cheapest: { title: string; price: string; location: string } | null;
}

export default function MarketPulse() {
  const [pulse, setPulse] = useState<Pulse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    api
      .get<RentalListResponse>("/rentals-db")
      .then((data) => {
        const priced = data.rentals.filter(
          (r) => typeof r.price_amount === "number"
        );
        const avg =
          priced.reduce((sum, r) => sum + (r.price_amount ?? 0), 0) /
          Math.max(priced.length, 1);
        const cheapest = [...priced].sort(
          (a, b) => (a.price_amount ?? 0) - (b.price_amount ?? 0)
        )[0];

        setPulse({
          listings: data.count,
          averageRent: Math.round(avg),
          cheapest: cheapest
            ? {
                title: cheapest.title,
                price: cheapest.price,
                location: cheapest.location,
              }
            : null,
        });
      })
      .catch(() => setError(true));
  }, []);

  if (error) {
    return (
      <div className="rounded-2xl border border-line bg-moss/60 p-6 text-sm text-ink-soft">
        Live market data is unavailable. Start the backend to see current
        listings here.
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-line bg-white p-6 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-widest text-evergreen">
        Live market pulse
      </p>

      <dl className="mt-4 grid grid-cols-2 gap-6">
        <div>
          <dt className="text-sm text-ink-soft">Listings tracked</dt>
          <dd className="font-display text-3xl font-600 text-ink">
            {pulse ? pulse.listings : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-sm text-ink-soft">Average asking rent</dt>
          <dd className="font-display text-3xl font-600 text-ink">
            {pulse ? `$${pulse.averageRent.toLocaleString()}` : "—"}
          </dd>
        </div>
      </dl>

      {pulse?.cheapest && (
        <div className="mt-6 border-t border-line pt-4">
          <p className="text-sm text-ink-soft">Lowest price right now</p>
          <p className="mt-1 truncate text-sm font-medium text-ink">
            {pulse.cheapest.price} · {pulse.cheapest.location}
          </p>
        </div>
      )}
    </div>
  );
}
