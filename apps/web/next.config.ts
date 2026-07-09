import type { NextConfig } from "next";

const isGhPages = process.env.GITHUB_PAGES === "true";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Static lab demo for GitHub Pages / portable hosting
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true,
  ...(isGhPages
    ? {
        basePath: "/BehaviorGraph",
        assetPrefix: "/BehaviorGraph",
      }
    : {}),
};

export default nextConfig;
