"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { BudgetAnalysis } from "@/lib/types";

const SLIDERS = [
  { key: "rent", label: "Rent", max: 5000, step: 50 },
  { key: "food", label: "Food & groceries", max: 1500, step: 25 },
  { key: "transport", label: "Transport", max: 800, step: 10 },
  { key: "utilities", label: "Utilities & internet", max: 800, step: 10 },
  { key: "other", label: "Everything else", max: 2000, step: 25 },
] as const;

type ExpenseKey = (typeof SLIDERS)[number]["key"];

const STATUS_STYLES: Record<BudgetAnalysis["status"], string> = {
  Comfortable: "bg-moss text-evergreen-deep",
  "Tight but survivable": "bg-amber-50 text-risk-mid",
  "Financially risky": "bg-red-50 text-risk-high",
};

const SEGMENT_SHADES = [
  "var(--evergreen-deep)",
  "var(--evergreen)",
  "#2b8377",
  "#4d9f94",
  "#7bbdb4",
];

const money = (n: number) =>
  `${n < 0 ? "-" : ""}$${Math.abs(n).toLocaleString("en-CA")}`;

export default function BudgetPage() {
  const [income, setIncome] = useState(4000);
  const [expenses, setExpenses] = useState<Record<ExpenseKey, number>>({
    rent: 2000,
    food: 500,
    transport: 150,
    utilities: 120,
    other: 300,
  });
  const [result, setResult] = useState<BudgetAnalysis | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const timer = setTimeout(async () => {
      try {
        const data = await api.post<BudgetAnalysis>("/budget-analysis", {
          income,
          ...expenses,
        });
        setResult(data);
        setFailed(false);
      } catch {
        setFailed(true);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [income, expenses]);

  const total = SLIDERS.reduce((sum, s) => sum + expenses[s.key], 0);
  const barBasis = Math.max(total, income, 1);

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <h1 className="font-display text-3xl font-700 text-ink">
        Can you afford Vancouver?
      </h1>
      <p className="mt-2 max-w-xl text-ink-soft">
        Set your monthly income and expenses. The verdict updates as you move
        the sliders.
      </p>

      <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_360px]">
        <div className="rounded-2xl border border-line bg-white p-6">
          <label className="block text-sm">
            <span className="mb-1 block font-medium text-ink">
              Monthly income after tax
            </span>
            <input
              type="number"
              min={0}
              value={income}
              onChange={(e) => setIncome(Math.max(0, Number(e.target.value)))}
              className="w-40 rounded-lg border border-line px-3 py-2 outline-none focus:border-evergreen"
            />
          </label>

          <div className="mt-8 space-y-6">
            {SLIDERS.map((s) => (
              <label key={s.key} className="block text-sm">
                <span className="mb-2 flex items-baseline justify-between">
                  <span className="font-medium text-ink">{s.label}</span>
                  <span className="font-display text-base font-600 text-evergreen">
                    {money(expenses[s.key])}
                  </span>
                </span>
                <input
                  type="range"
                  min={0}
                  max={s.max}
                  step={s.step}
                  value={expenses[s.key]}
                  onChange={(e) =>
                    setExpenses((prev) => ({
                      ...prev,
                      [s.key]: Number(e.target.value),
                    }))
                  }
                  className="w-full accent-evergreen"
                />
              </label>
            ))}
          </div>
        </div>

        <aside className="h-fit rounded-2xl border border-line bg-white p-6 lg:sticky lg:top-24">
          {failed ? (
            <p className="text-risk-high">
              Couldn&apos;t reach the server. Make sure the backend is running.
            </p>
          ) : (
            <>
              <span
                className={`inline-block rounded-full px-3 py-1 text-sm font-semibold ${
                  result ? STATUS_STYLES[result.status] : "bg-moss text-ink-soft"
                }`}
              >
                {result?.status ?? "Calculating…"}
              </span>

              <dl className="mt-6 space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Income</dt>
                  <dd className="font-medium text-ink">{money(income)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-ink-soft">Total expenses</dt>
                  <dd className="font-medium text-ink">{money(total)}</dd>
                </div>
                <div className="flex justify-between border-t border-line pt-3">
                  <dt className="font-medium text-ink">Left over</dt>
                  <dd
                    className={`font-display text-lg font-700 ${
                      income - total < 0 ? "text-risk-high" : "text-evergreen"
                    }`}
                  >
                    {money(income - total)}
                  </dd>
                </div>
              </dl>

              <div className="mt-6">
                <div className="flex h-3 overflow-hidden rounded-full bg-moss">
                  {SLIDERS.map((s, i) => (
                    <div
                      key={s.key}
                      title={`${s.label}: ${money(expenses[s.key])}`}
                      style={{
                        width: `${(expenses[s.key] / barBasis) * 100}%`,
                        background: SEGMENT_SHADES[i],
                      }}
                    />
                  ))}
                </div>
                <ul className="mt-4 space-y-1.5 text-xs text-ink-soft">
                  {SLIDERS.map((s, i) => (
                    <li key={s.key} className="flex items-center gap-2">
                      <span
                        className="size-2.5 shrink-0 rounded-full"
                        style={{ background: SEGMENT_SHADES[i] }}
                      />
                      <span className="flex-1">{s.label}</span>
                      <span>
                        {total ? Math.round((expenses[s.key] / total) * 100) : 0}
                        %
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              {income > 0 && expenses.rent / income > 0.3 && (
                <p className="mt-6 rounded-lg bg-moss p-3 text-xs text-ink-soft">
                  Rent is {Math.round((expenses.rent / income) * 100)}% of your
                  income. The common guideline is to stay under 30%.
                </p>
              )}
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
