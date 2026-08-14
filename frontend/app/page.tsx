import Link from "next/link";
import MarketPulse from "@/components/MarketPulse";

const features = [
  {
    title: "Search with judgment",
    body: "Filter live Metro Vancouver listings by budget and area, ranked by real affordability instead of raw price.",
  },
  {
    title: "Know the market",
    body: "CMHC vacancy rates and rent trends by neighbourhood, so you negotiate with data instead of guesses.",
  },
  {
    title: "Spot the scams",
    body: "Every listing is screened for pressure tactics, off-market prices, and payment red flags before you reach out.",
  },
];

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl px-6">
      <section className="grid items-center gap-12 py-20 md:grid-cols-2 md:py-28">
        <div>
          <h1 className="font-display text-4xl font-700 leading-tight tracking-tight text-ink md:text-5xl">
            Find a better place to live in Metro&nbsp;Vancouver.
          </h1>
          <p className="mt-5 max-w-md text-lg text-ink-soft">
            RentScout combines live listings, CMHC market data, affordability
            analysis, and AI recommendations — so you rent with evidence, not
            luck.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              href="/search"
              className="rounded-full bg-evergreen px-6 py-3 text-sm font-semibold text-paper transition-colors hover:bg-evergreen-deep"
            >
              Find rentals
            </Link>
            <Link
              href="/budget"
              className="rounded-full border border-line px-6 py-3 text-sm font-semibold text-ink transition-colors hover:border-evergreen hover:text-evergreen"
            >
              Analyze my budget
            </Link>
          </div>
        </div>

        <MarketPulse />
      </section>

      <section className="grid gap-6 pb-8 md:grid-cols-3">
        {features.map((f) => (
          <div
            key={f.title}
            className="rounded-2xl border border-line bg-white p-6"
          >
            <h2 className="font-display text-lg font-600 text-ink">
              {f.title}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-ink-soft">
              {f.body}
            </p>
          </div>
        ))}
      </section>
    </div>
  );
}
