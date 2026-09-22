"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const LINKS = [
  { href: "/", label: "홈 (현재 날씨·지도)" },
  { href: "/forecast", label: "AI 예측" },
  { href: "/history", label: "날짜별 날씨" },
  { href: "/anomalies", label: "이상치" },
];

export default function Nav() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-3 sm:px-8">
        <Link href="/" className="font-bold" onClick={() => setOpen(false)}>
          Weather AI
        </Link>
        <button
          onClick={() => setOpen((v) => !v)}
          aria-label="메뉴 열기"
          aria-expanded={open}
          className="rounded p-2 text-2xl leading-none hover:bg-gray-100"
        >
          ☰
        </button>
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
