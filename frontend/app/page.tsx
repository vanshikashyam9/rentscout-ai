import Link from "next/link";
import MarketPulse from "@/components/MarketPulse";

const features = [
  {
    title: "Screen any listing",
    body: "Paste a listing you found anywhere — Craigslist, Marketplace, a WhatsApp group. RentScout checks it for pressure tactics, payment red flags, and prices that undercut the whole neighbourhood.",
    href: "/analyze",
    cta: "Check a listing",
  },
  {
    title: "Know the market",
    body: "Real CMHC vacancy rates and trends by neighbourhood, back to 2022 — so you know whether to move fast or negotiate.",
    href: "/market",
    cta: "See the data",
  },
  {
    title: "Know what you can afford",
    body: "Set your income and expenses against real Metro Vancouver costs, and see what rent actually leaves you room to live.",
    href: "/budget",
    cta: "Plan a budget",
  },
];

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl px-6">
      <section className="grid items-center gap-12 py-20 md:grid-cols-2 md:py-28">
        <div>
          <h1 className="font-display text-4xl font-700 leading-tight tracking-tight text-ink md:text-5xl">
            Before you send that deposit, check the listing.
          </h1>
          <p className="mt-5 max-w-md text-lg text-ink-soft">
            Rental scams target newcomers to Metro&nbsp;Vancouver hardest.
            RentScout screens any listing you find for red flags, then shows you
            the real CMHC market data and what you can actually afford.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              href="/analyze"
              className="rounded-full bg-evergreen px-6 py-3 text-sm font-semibold text-paper transition-colors hover:bg-evergreen-deep"
            >
              Check a listing
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
            className="flex flex-col rounded-2xl border border-line bg-white p-6"
          >
            <h2 className="font-display text-lg font-600 text-ink">
              {f.title}
            </h2>
            <p className="mt-2 flex-1 text-sm leading-relaxed text-ink-soft">
              {f.body}
            </p>
            <Link
              href={f.href}
              className="mt-4 text-sm font-semibold text-evergreen hover:text-evergreen-deep"
            >
              {f.cta} →
            </Link>
          </div>
        ))}
      </section>

      <section className="mb-16 rounded-2xl border border-line bg-moss/50 p-6">
        <h2 className="font-display text-base font-600 text-ink">
          Where the numbers come from
        </h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-ink-soft">
          RentScout is not a listings site — it does not host rentals or
          republish them from other platforms. It checks the listing you bring
          to it, wherever you found it. Every figure quoted here comes from
          CMHC&apos;s annual Rental Market Survey: vacancy rates and average
          rents by neighbourhood and unit size, published by the federal
          housing agency and verifiable at{" "}
          <span className="font-medium text-ink">cmhc-schl.gc.ca</span>.
        </p>
      </section>
    </div>
  );
}
