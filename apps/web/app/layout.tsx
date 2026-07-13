import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BehaviorGraph — Behavioral Analytics Studio",
  description:
    "Portfolio lab: event taxonomy, nested activation funnel, retention cohorts, journey graph and product opportunity memos on synthetic SaaS events.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
