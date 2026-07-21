import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Job-Agent",
  description: "Local-first AI job search & application management platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
