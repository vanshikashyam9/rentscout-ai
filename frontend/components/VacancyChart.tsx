"use client";

import { useState } from "react";
import type { VacancyPoint } from "@/lib/types";

/**
 * Vacancy rate over time for one area.
 *
 * Single series, so there is no legend — the heading names what is plotted.
 * Only the final point is directly labelled; the axis and the hover tooltip
 * carry the rest.
 */

const W = 720;
const H = 280;
const PAD = { top: 24, right: 60, bottom: 36, left: 44 };

const INNER_W = W - PAD.left - PAD.right;
const INNER_H = H - PAD.top - PAD.bottom;

const TICK_STEPS = [0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10];

/** Round the axis top up to a clean 1 / 2 / 5 step so ticks read evenly. */
function niceMax(value: number) {
  const target = Math.max(value * 1.2, 1);
  const magnitude = 10 ** Math.floor(Math.log10(target));
  const step = [1, 2, 2.5, 5, 10].find((s) => s * magnitude >= target) ?? 10;
  return step * magnitude;
}

/** Whole-number ticks where possible — 0/1/2/3 reads better than 0/1.25/2.5. */
function axisTicks(max: number) {
  const step = TICK_STEPS.find((s) => max / s <= 5) ?? max / 4;
  const out: number[] = [];
  for (let v = 0; v <= max + 1e-9; v += step) out.push(+v.toFixed(2));
  return out;
}

export default function VacancyChart({ series }: { series: VacancyPoint[] }) {
  const [hovered, setHovered] = useState<number | null>(null);

  if (series.length === 0) return null;

  const yMax = niceMax(Math.max(...series.map((d) => d.vacancy_rate)));

  const x = (i: number) =>
    series.length === 1
      ? PAD.left + INNER_W / 2
      : PAD.left + (i * INNER_W) / (series.length - 1);

  const y = (v: number) => PAD.top + INNER_H - (v / yMax) * INNER_H;

  const points = series.map((d, i) => ({ ...d, cx: x(i), cy: y(d.vacancy_rate) }));
  const linePath = points.map((p) => `${p.cx},${p.cy}`).join(" ");
  const areaPath = `${PAD.left},${PAD.top + INNER_H} ${linePath} ${
    points[points.length - 1].cx
  },${PAD.top + INNER_H}`;

  const ticks = axisTicks(yMax);
  const last = points[points.length - 1];
  const active = hovered === null ? null : points[hovered];

  return (
    <figure className="m-0">
      <div className="relative">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="w-full"
          role="img"
          aria-label={`Vacancy rate from ${series[0].year} to ${
            series[series.length - 1].year
          }`}
        >
          {/* Recessive hairline gridlines */}
          {ticks.map((t) => (
            <g key={t}>
              <line
                x1={PAD.left}
                x2={PAD.left + INNER_W}
                y1={y(t)}
                y2={y(t)}
                stroke="var(--line)"
                strokeWidth={1}
              />
              <text
                x={PAD.left - 10}
                y={y(t) + 4}
                textAnchor="end"
                className="fill-ink-soft text-[11px] tabular-nums"
              >
                {t}%
              </text>
            </g>
          ))}

          {/* Area wash under the line */}
          <polygon points={areaPath} fill="var(--evergreen)" opacity={0.1} />

          <polyline
            points={linePath}
            fill="none"
            stroke="var(--evergreen)"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
          />

          {/* Crosshair on the hovered year */}
          {active && (
            <line
              x1={active.cx}
              x2={active.cx}
              y1={PAD.top}
              y2={PAD.top + INNER_H}
              stroke="var(--evergreen)"
              strokeWidth={1}
              opacity={0.35}
            />
          )}

          {points.map((p, i) => (
            <circle
              key={p.year}
              cx={p.cx}
              cy={p.cy}
              r={hovered === i ? 6 : 4.5}
              fill="var(--evergreen)"
              stroke="var(--paper)"
              strokeWidth={2}
            />
          ))}

          {/* Only the endpoint is directly labelled */}
          <text
            x={last.cx + 12}
            y={last.cy + 4}
            className="fill-ink text-[13px] font-semibold tabular-nums"
          >
            {last.vacancy_rate}%
          </text>

          {points.map((p) => (
            <text
              key={p.year}
              x={p.cx}
              y={PAD.top + INNER_H + 22}
              textAnchor="middle"
              className="fill-ink-soft text-[11px] tabular-nums"
            >
              {p.year}
            </text>
          ))}

          {/* Hit targets, wider than the dots */}
          {points.map((p, i) => (
            <rect
              key={p.year}
              x={p.cx - INNER_W / (series.length * 2)}
              y={PAD.top}
              width={INNER_W / series.length}
              height={INNER_H}
              fill="transparent"
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
            />
          ))}
        </svg>

        {active && (
          <div
            className="pointer-events-none absolute -translate-x-1/2 -translate-y-full rounded-lg border border-line bg-white px-3 py-2 text-xs shadow-sm"
            style={{
              left: `${(active.cx / W) * 100}%`,
              top: `${(active.cy / H) * 100}%`,
            }}
          >
            <div className="font-semibold text-ink">{active.year}</div>
            <div className="text-ink-soft tabular-nums">
              {active.vacancy_rate}% vacancy
            </div>
          </div>
        )}
      </div>
    </figure>
  );
}
