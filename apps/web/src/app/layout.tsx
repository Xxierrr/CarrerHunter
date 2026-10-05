import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Internship Intelligence — Find Your Perfect Internship",
  description:
    "AI-powered internship discovery platform that continuously finds opportunities, determines your eligibility, and notifies you about relevant matches.",
  keywords: ["internship", "jobs", "career", "AI", "job search", "eligibility"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
