import type { Metadata } from "next";
import { Syne, Outfit } from "next/font/google";
import { SmoothScroll } from "@/components/SmoothScroll";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

const syne = Syne({
  variable: "--font-syne",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Ethos - Project division 4.0",
  description: "Ethos - Project division 4.0",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`dark scroll-smooth ${outfit.variable} ${syne.variable}`}>
      <body
        className="antialiased bg-black text-white font-sans selection:bg-white selection:text-black overflow-x-hidden"
      >
        <SmoothScroll>
          {children}
        </SmoothScroll>
      </body>
    </html>
  );
}
