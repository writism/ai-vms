import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { JotaiProvider } from "@/components/providers/JotaiProvider";
import { SWRProvider } from "@/components/providers/SWRProvider";
import { AppLayout } from "@/ui/layout/AppLayout";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI-VMS",
  description: "AI Multi-Agent 기반 영상 관리/관제 시스템",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="ko"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full">
        <JotaiProvider>
          <SWRProvider>
            <AppLayout>{children}</AppLayout>
          </SWRProvider>
        </JotaiProvider>
      </body>
    </html>
  );
}
