import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BehaviorGraph — Behavioral Analytics Studio",
  description:
    "Turn product events into journeys, activation funnels, retention cohorts, friction signals and opportunity memos.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
