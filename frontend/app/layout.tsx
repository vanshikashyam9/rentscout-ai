import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "RentScout — Rental intelligence for Metro Vancouver",
  description:
    "Live listings, market data, affordability analysis, and AI recommendations for renters in Metro Vancouver.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sora:wght@500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen antialiased">
        <Navbar />
        <main>{children}</main>
        <footer className="border-t border-line mt-24 py-10 text-center text-sm text-ink-soft">
          RentScout · Rental intelligence for Metro Vancouver
        </footer>
      </body>
    </html>
  );
}
