"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const LINKS = [
  { href: "/", label: "홈 (현재 날씨·지도)" },
  { href: "/predict", label: "오늘의 날씨 예상해보기" },
  { href: "/forecast", label: "AI 예측" },
  { href: "/history", label: "날짜별 날씨" },
  { href: "/anomalies", label: "이상치" },
];

export default function Nav() {
  const [open, setOpen] = useState(false);
  const [waking, setWaking] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    // 무료 호스팅은 오래 쉬면 서버가 잠드는데, 페이지를 열자마자 미리 깨워두면
    // 실제로 지도/위치 버튼을 누를 때는 이미 깨어있어 훨씬 빠르게 느껴진다.
    let cancelled = false;
    const wakeTimer = setTimeout(() => !cancelled && setWaking(true), 1500);
    fetch(`${API_BASE_URL}/health`)
      .catch(() => {})
      .finally(() => {
        cancelled = true;
        clearTimeout(wakeTimer);
        setWaking(false);
      });
    return () => {
      cancelled = true;
      clearTimeout(wakeTimer);
    };
  }, []);

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-3 sm:px-8">
        <Link href="/" className="font-bold" onClick={() => setOpen(false)}>
          Weather AI
        </Link>
        <div className="flex items-center gap-2">
          {waking && (
            <span className="text-xs text-gray-400">서버 깨우는 중...</span>
          )}
          <button
            onClick={() => setOpen((v) => !v)}
            aria-label="메뉴 열기"
            aria-expanded={open}
            className="rounded p-2 text-2xl leading-none hover:bg-gray-100"
          >
            ☰
          </button>
        </div>
      </div>
      {open && (
        <nav className="border-t border-gray-200 bg-white">
          <ul className="mx-auto max-w-3xl px-4 py-2 sm:px-8">
            {LINKS.map((l) => (
              <li key={l.href}>
                <Link
                  href={l.href}
                  onClick={() => setOpen(false)}
                  className={`block rounded px-2 py-2 text-sm ${
                    pathname === l.href
                      ? "font-semibold text-blue-600"
                      : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  {l.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </header>
  );
}
