"use client";

import { useEffect, useState } from "react";

import ForecastPanel from "@/components/ForecastPanel";
import StationSelect from "@/components/StationSelect";
import { type Forecast, type Observation, getCurrentWeather, getForecast } from "@/lib/api";
import { useSelectedStation } from "@/lib/useStation";

export default function ForecastPage() {
  const [stationId, setStationId] = useSelectedStation();
  const [forecasts, setForecasts] = useState<Forecast[]>([]);
  const [observation, setObservation] = useState<Observation | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([getForecast(stationId), getCurrentWeather(stationId)]).then(([f, o]) => {
      if (!cancelled) {
        setForecasts(f);
        setObservation(o);
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
        <h1 className="text-2xl font-bold">AI 예측 (지도학습 모델)</h1>
        <p className="text-sm text-gray-600">
          과거 5년치 관측자료로 학습한 XGBoost 모델이 몇 시간 뒤 기온을 예측합니다.
        </p>
      </header>

      <StationSelect stationId={stationId} onChange={setStationId} />

      {loading && <p className="text-sm text-gray-400">불러오는 중...</p>}
      <ForecastPanel forecasts={forecasts} observation={observation} />
    </main>
  );
}
