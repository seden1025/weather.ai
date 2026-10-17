import type { Metadata } from "next";

// 관리자 화면은 검색에 노출되지 않게 한다. (메뉴에도 링크하지 않는다)
export const metadata: Metadata = {
  title: "관리자 - Weather AI",
  robots: { index: false, follow: false },
};

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return children;
}
