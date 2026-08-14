import Link from "next/link";

// Only routes that exist. /login ships later — add it back here when it lands,
// so the live site never links to a 404.
const links = [
  { href: "/search", label: "Find rentals" },
  { href: "/budget", label: "Budget" },
  { href: "/market", label: "Market" },
  { href: "/analyze", label: "Scam check" },
];

export default function Navbar() {
  return (
    <header className="border-b border-line bg-paper/90 backdrop-blur sticky top-0 z-10">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link
          href="/"
          className="font-display text-lg font-700 tracking-tight text-ink"
        >
          Rent<span className="text-evergreen">Scout</span>
        </Link>

        <div className="hidden gap-7 text-sm font-medium text-ink-soft sm:flex">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="transition-colors hover:text-evergreen"
            >
              {l.label}
            </Link>
          ))}
        </div>

        <Link
          href="/search"
          className="rounded-full border border-evergreen px-4 py-1.5 text-sm font-medium text-evergreen transition-colors hover:bg-evergreen hover:text-paper"
        >
          Get started
        </Link>
      </nav>
    </header>
  );
}
