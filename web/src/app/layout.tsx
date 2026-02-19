import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Meme Coin Analytics | The Last 6 Months",
  description:
    "Publication-quality econometric analysis of meme coin markets — launches, survival rates, returns, and who profits. Powered by Codex.io.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-white">
        {children}
      </body>
    </html>
  );
}
