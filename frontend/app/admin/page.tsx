"use client";

import { useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function stamp(d: Date) {
  const p = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}`;
}

export default function AdminPage() {
  // 토큰은 이 화면의 메모리에만 두고 브라우저에 저장하지 않는다. (새로고침하면 다시 입력)
  const [token, setToken] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);

  async function handleDownload(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setDone(null);
    if (start && end && start > end) {
      setError("시작일이 종료일보다 늦어요.");
      return;
    }
    setBusy(true);
    try {
      const url = new URL(`${API_BASE_URL}/admin/export/predictions.xlsx`);
      if (start) url.searchParams.set("start", start);
      if (end) url.searchParams.set("end", end);
      const res = await fetch(url.toString(), {
        headers: { "X-Admin-Token": token.trim() },
        cache: "no-store",
      });
      if (res.status === 401) {
        setError("관리자 토큰이 올바르지 않아요.");
        return;
      }
      if (res.status === 404) {
        setError("서버에 ADMIN_TOKEN이 설정되어 있지 않아요. 백엔드 환경변수를 먼저 확인해주세요.");
        return;
      }
      if (!res.ok) {
        setError("내려받지 못했어요. 잠시 후 다시 시도해주세요.");
        return;
      }
      const blob = await res.blob();
      const name = `weather-ai-responses-${stamp(new Date())}.xlsx`;
      const href = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = href;
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(href);
      setDone(`${name} 파일을 내려받았어요.`);
    } catch {
      setError(
        "서버에 연결하지 못했어요. 잠시 후 다시 시도해주세요 (서버가 방금 깨어난 경우 최대 1분 걸릴 수 있어요)."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto max-w-md space-y-6 p-8">
      <header className="space-y-2 border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold">설문 응답 엑셀로 받기</h1>
        <p className="text-sm text-gray-600">
          지금까지 제출된 예측·근거·실제 결과 비교를 엑셀 파일(.xlsx)로 내려받아요. 누를
          때마다 그 시점의 최신 데이터로 새로 만들어져요.
        </p>
      </header>

      <form onSubmit={handleDownload} className="space-y-4 rounded-xl border border-gray-200 p-5">
        <div>
          <label htmlFor="token" className="mb-1 block text-sm font-medium text-gray-700">
            관리자 토큰
          </label>
          <input
            id="token"
            type="password"
            autoComplete="off"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />
          <p className="mt-1 text-xs text-gray-400">백엔드에 설정한 ADMIN_TOKEN 값이에요.</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label htmlFor="start" className="mb-1 block text-sm font-medium text-gray-700">
              시작일 (선택)
            </label>
            <input
              id="start"
              type="date"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label htmlFor="end" className="mb-1 block text-sm font-medium text-gray-700">
              종료일 (선택)
            </label>
            <input
              id="end"
              type="date"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <p className="text-xs text-gray-400">비워두면 전체 기간이에요. 기준은 예측한 날짜예요.</p>

        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}
        {done && <p className="text-sm text-green-700">{done}</p>}

        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {busy ? "파일 만드는 중..." : "엑셀 파일 내려받기"}
        </button>
      </form>

      <p className="text-xs text-gray-500">
        파일에는 보상 연락처(동의한 응답만)가 들어 있어요. 내려받은 파일은 다른 사람과 공유하지
        말고, 보상 안내가 끝나면 삭제해주세요.
      </p>
    </main>
  );
}
