import type { Metadata } from "next";
import { Inter, Patrick_Hand } from "next/font/google";
import Script from "next/script";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const patrickHand = Patrick_Hand({
  weight: "400",
  variable: "--font-patrick",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Scribbl | Turn PDFs into Sketch Videos",
    template: "%s | Scribbl"
  },
  description: "Transform boring PDFs and textbooks into engaging, hand-drawn sketch videos instantly. The fastest way to study.",
  keywords: ["study tool", "pdf to video", "ai education", "sketch video", "visual learning", "vanderbilt"],
  authors: [{ name: "Scribbl Team" }],
  creator: "Scribbl",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://scribbl.study",
    title: "Scribbl - Turn PDFs into Sketch Videos",
    description: "Transform boring PDFs and textbooks into engaging, hand-drawn sketch videos instantly.",
    siteName: "Scribbl",
    images: [
      {
        url: "/og-image.png", // We should probably generate this or use a placeholder
        width: 1200,
        height: 630,
        alt: "Scribbl Preview",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Scribbl - Turn PDFs into Sketch Videos",
    description: "Transform boring PDFs and textbooks into engaging, hand-drawn sketch videos instantly.",
    creator: "@scribblstudy",
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${patrickHand.variable} antialiased`}
      >
        {children}
        <Script src="https://www.googletagmanager.com/gtag/js?id=G-4Y93C7108Z" strategy="afterInteractive" />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-4Y93C7108Z');
          `}
        </Script>
      </body>
    </html>
  );
}
