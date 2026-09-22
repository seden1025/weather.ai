"use client";

import { useState } from "react";

import RecentHistory from "@/components/RecentHistory";
import StationSelect from "@/components/StationSelect";
import { type Observation, getOnDate } from "@/lib/api";
import { useSelectedStation } from "@/lib/useStation";

function todayIso() {
  const d = new Date();
  const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}

export default function HistoryPage() {
  const [stationId, setStationId] = useSelectedStation();
  const [date, setDate] = useState(todayIso());
  const [observations, setObservations] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  async function handleSearch() {
    setLoading(true);
    setSearched(true);
    const data = await getOnDate(stationId, date);
    setObservations(data);
    setLoading(false);
  }

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-8">
      <header className="space-y-2 border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold">날짜별 날씨</h1>
        <p className="text-sm text-gray-600">
          원하는 날짜의 시간별 날씨를 조회합니다. DB에 없는 날짜는 기상청에서 즉시
          받아와 채운 뒤 보여줍니다.
        </p>
      </header>

      <div className="flex flex-wrap items-center gap-3">
        <StationSelect stationId={stationId} onChange={setStationId} />
        <input
          type="date"
          value={date}
          max={todayIso()}
          onChange={(e) => setDate(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "조회 중..." : "조회"}
        </button>
      </div>

      {searched && !loading && observations.length === 0 && (
        <p className="text-sm text-red-600">해당 날짜의 데이터를 찾을 수 없습니다.</p>
      )}
      {observations.length > 0 && <RecentHistory observations={observations} />}
    </main>
  );
}
