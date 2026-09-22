"use client";

import { useEffect, useState } from "react";

import AnomalyPanel from "@/components/AnomalyPanel";
import StationSelect from "@/components/StationSelect";
import { type AnomalyEvent, getAnomalyEvents } from "@/lib/api";
import { useSelectedStation } from "@/lib/useStation";

export default function AnomaliesPage() {
  const [stationId, setStationId] = useSelectedStation();
  const [anomalies, setAnomalies] = useState<AnomalyEvent[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getAnomalyEvents(stationId).then((data) => {
      if (!cancelled) {
        setAnomalies(data);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [stationId]);

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-8">
      <header className="space-y-2 border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold">감지된 이상치</h1>
        <p className="text-sm text-gray-600">
          평년과 크게 다른 값이 관측되면 과거 유사 사례와 관련 뉴스를 함께 정리해 보여줍니다.
        </p>
      </header>

      <StationSelect stationId={stationId} onChange={setStationId} />

      {loading && <p className="text-sm text-gray-400">불러오는 중...</p>}
      <AnomalyPanel events={anomalies} />
    </main>
  );
}
