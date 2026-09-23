import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { SmoothScrolling } from "@/components/SmoothScrolling";
import { ThemeToggle } from "@/components/ThemeToggle";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "InboxPilot",
  description: "Your inbox, on autopilot.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${outfit.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col font-sans">
        <SmoothScrolling>
          <AuthProvider>
            <ThemeToggle />
            {children}
          </AuthProvider>
        </SmoothScrolling>
      </body>
    </html>
  );
}
