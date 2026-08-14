import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emits .next/standalone with only the files the server needs, so the
  // production image doesn't ship node_modules.
  output: "standalone",
};

export default nextConfig;
