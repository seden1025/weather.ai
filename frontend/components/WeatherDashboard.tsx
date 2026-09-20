"use client";

import { useEffect, useMemo, useState } from "react";

import AnomalyPanel from "@/components/AnomalyPanel";
import RecentHistory from "@/components/RecentHistory";
import WeatherCard from "@/components/WeatherCard";
import {
  type AnomalyEvent,
  type Observation,
  type Station,
  getAnomalyEvents,
  getCurrentWeather,
  getNearestStation,
  getRecentHistory,
  getStations,
} from "@/lib/api";

const RECENT_HOURS = 5;
const DEFAULT_STATION_ID = "108"; // 서울

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function ingestStation(stationId: string) {
  await fetch(`${API_BASE_URL}/weather/ingest/${stationId}?hours=24`, { method: "POST" });
}

export default function WeatherDashboard() {
  const [stations, setStations] = useState<Station[]>([]);
  const [stationId, setStationId] = useState(DEFAULT_STATION_ID);
  const [observation, setObservation] = useState<Observation | null>(null);
  const [recent, setRecent] = useState<Observation[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);

  useEffect(() => {
    getStations().then(setStations);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      let current = await getCurrentWeather(stationId);
      if (!current) {
        await ingestStation(stationId);
        current = await getCurrentWeather(stationId);
      }
      const [recentHistory, anomalyEvents] = await Promise.all([
        getRecentHistory(stationId, RECENT_HOURS),
        getAnomalyEvents(stationId),
      ]);
      if (!cancelled) {
        setObservation(current);
        setRecent(recentHistory);
        setAnomalies(anomalyEvents);
        setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [stationId]);

  const stationName = useMemo(
    () => stations.find((s) => s.id === stationId)?.name ?? stationId,
    [stations, stationId]
  );

  function handleLocate() {
    if (!navigator.geolocation) {
      setLocationError("이 브라우저는 위치 조회를 지원하지 않습니다.");
      return;
    }
    setLocating(true);
    setLocationError(null);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const nearest = await getNearestStation(pos.coords.latitude, pos.coords.longitude);
        if (nearest) setStationId(nearest.id);
        else setLocationError("가까운 지점을 찾지 못했습니다.");
        setLocating(false);
      },
      () => {
        setLocationError("위치 권한이 거부되었거나 조회에 실패했습니다.");
        setLocating(false);
      }
    );
  }

  return (
    <div className="space-y-8">
      <section className="flex flex-wrap items-center gap-3">
        <select
          value={stationId}
          onChange={(e) => setStationId(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
        >
          {stations.length === 0 && <option value={stationId}>{stationName}</option>}
          {stations.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
        <button
          onClick={handleLocate}
          disabled={locating}
          className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {locating ? "위치 확인 중..." : "내 위치로 찾기"}
        </button>
        {locationError && <span className="text-sm text-red-600">{locationError}</span>}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">
          {stationName} 현재 날씨 {loading && <span className="text-sm text-gray-400">(불러오는 중...)</span>}
        </h2>
        <WeatherCard observation={observation} />
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">최근 {RECENT_HOURS}시간 날씨</h2>
        <RecentHistory observations={recent} />
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">감지된 이상치</h2>
        <AnomalyPanel events={anomalies} />
      </section>
    </div>
  );
}
