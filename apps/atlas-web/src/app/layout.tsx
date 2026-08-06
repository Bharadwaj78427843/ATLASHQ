import type { Metadata } from "next";
import { AuthProvider } from "@/contexts/AuthContext";
import "./globals.css";

export const metadata: Metadata = {
  title: "AtlasHQ - AI Engineering Operating System",
  description: "The Atlas platform for software teams",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className="h-full antialiased dark"
      style={{
        ["--font-inter" as string]: "ui-sans-serif, system-ui, sans-serif",
        ["--font-jetbrains-mono" as string]: "ui-monospace, SFMono-Regular, monospace",
      }}
    >
      <body className="min-h-full bg-[var(--color-background)] text-[var(--color-text-primary)]">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}