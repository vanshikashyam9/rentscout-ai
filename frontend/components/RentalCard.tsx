import type { Rental } from "@/lib/types";

/** A single rental listing. Match score + reasons show only when provided. */
export default function RentalCard({
  rental,
  score,
  reasons,
}: {
  rental: Rental;
  score?: number;
  reasons?: string[];
}) {
  return (
    <article className="flex flex-col rounded-2xl border border-line bg-white p-5 transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <span className="font-display text-xl font-600 text-ink">
          {rental.price}
          <span className="text-sm font-400 text-ink-soft">/mo</span>
        </span>

        {typeof score === "number" && (
          <span className="shrink-0 rounded-full bg-moss px-2.5 py-1 text-xs font-semibold text-evergreen-deep">
            Match {score}
          </span>
        )}
      </div>

      <h3 className="mt-2 line-clamp-2 text-sm font-medium text-ink">
        {rental.title}
      </h3>
      <p className="mt-1 text-sm text-ink-soft">
        {rental.location}
        {typeof rental.bedrooms === "number" && (
          <> · {rental.bedrooms === 0 ? "Studio" : `${rental.bedrooms} bed`}</>
        )}
      </p>

      {reasons && reasons.length > 0 && (
        <ul className="mt-3 space-y-1">
          {reasons.map((r) => (
            <li key={r} className="flex gap-1.5 text-xs text-ink-soft">
              <span className="text-evergreen">✓</span>
              {r}
            </li>
          ))}
        </ul>
      )}

      {/* Demo rows describe units that do not exist, so they must never be
          rendered as a link to a real posting. */}
      {rental.source === "demo" ? (
        <p className="mt-4 text-xs text-ink-soft">
          Sample listing — for demonstration
        </p>
      ) : (
        <a
          href={rental.link}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 text-sm font-semibold text-evergreen hover:text-evergreen-deep"
        >
          View listing →
        </a>
      )}
    </article>
  );
}
