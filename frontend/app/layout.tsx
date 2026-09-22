import type { Metadata } from "next";

import Nav from "@/components/Nav";

import "./globals.css";

export const metadata: Metadata = {
  title: "Weather AI",
  description: "지도학습 기반 날씨 예측 AI 서비스",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <Nav />
        {children}
      </body>
    </html>
  );
}
