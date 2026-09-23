"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";

import AddressSearch from "@/components/AddressSearch";
import RecentHistory from "@/components/RecentHistory";
import StationSelect from "@/components/StationSelect";
import WeatherCard from "@/components/WeatherCard";
import { useSelectedStation } from "@/lib/useStation";
import {
  type Observation,
  type Station,
  getCurrentWeather,
  getNearestStation,
  getRecentHistory,
  getStations,
} from "@/lib/api";

const RECENT_HOURS = 5;

const WeatherMap = dynamic(() => import("@/components/WeatherMap"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[360px] items-center justify-center rounded-xl border border-gray-200 text-sm text-gray-400">
      지도를 불러오는 중...
    </div>
  ),
});

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function ingestStation(stationId: string) {
  await fetch(`${API_BASE_URL}/weather/ingest/${stationId}?hours=24`, { method: "POST" });
}

export default function WeatherDashboard() {
  const [stationId, setStationId] = useSelectedStation();
  const [stations, setStations] = useState<Station[]>([]);
  const [observation, setObservation] = useState<Observation | null>(null);
  const [recent, setRecent] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [flyToCenter, setFlyToCenter] = useState<[number, number] | null>(null);
  const [searchLabel, setSearchLabel] = useState<string | null>(null);

  useEffect(() => {
    getStations().then(setStations);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      let current = await getCurrentWeather(stationId);
      const staleMs = current ? Date.now() - new Date(current.observed_at).getTime() : Infinity;
      const isStale = staleMs > 90 * 60 * 1000; // 90분 넘게 갱신 안 됐으면 새로 받아옴
      if (!current || isStale) {
        await ingestStation(stationId);
        current = await getCurrentWeather(stationId);
      }
      const recentHistory = await getRecentHistory(stationId, RECENT_HOURS);
      if (!cancelled) {
        setObservation(current);
        setRecent(recentHistory);
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
        const { latitude, longitude, accuracy } = pos.coords;
        const nearest = await getNearestStation(latitude, longitude);
        if (nearest) {
          setStationId(nearest.id);
          setFlyToCenter([latitude, longitude]);
          const accuracyNote = accuracy ? ` (오차범위 ±${Math.round(accuracy)}m)` : "";
          setSearchLabel(`내 위치${accuracyNote}`);
        } else {
          setLocationError("가까운 지점을 찾지 못했습니다.");
        }
        setLocating(false);
      },
      (err) => {
        setLocationError(
          err.code === err.PERMISSION_DENIED
            ? "위치 권한이 거부되었습니다. 브라우저 주소창 왼쪽 아이콘에서 위치 권한을 허용해주세요."
            : "위치 조회에 실패했습니다."
        );
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  }

  async function handleAddressFound(lat: number, lon: number, label: string) {
    const nearest = await getNearestStation(lat, lon);
    setFlyToCenter([lat, lon]);
    if (nearest) {
      setSearchLabel(`${label} (가장 가까운 지점까지 약 ${nearest.distance_km}km)`);
      setStationId(nearest.id);
    } else {
      setSearchLabel(label);
    }
  }

  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <AddressSearch onFound={handleAddressFound} />

        <div className="flex flex-wrap items-center gap-3">
          <StationSelect
            stationId={stationId}
            onChange={(id) => {
              setStationId(id);
              setSearchLabel(null);
            }}
          />
          <button
            onClick={handleLocate}
            disabled={locating}
            className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {locating ? "위치 확인 중..." : "내 위치로 찾기"}
          </button>
          {locationError && <span className="text-sm text-red-600">{locationError}</span>}
        </div>

        {searchLabel && (
          <p className="text-sm text-gray-500">
            검색 위치: {searchLabel} → 가장 가까운 관측지점 <strong>{stationName}</strong>
          </p>
        )}

        <WeatherMap
          stations={stations}
          onSelectStation={(id) => {
            setStationId(id);
            setSearchLabel(null);
          }}
          flyToCenter={flyToCenter}
        />
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">
          {stationName} 현재 날씨{" "}
          {loading && <span className="text-sm text-gray-400">(불러오는 중...)</span>}
        </h2>
        <WeatherCard observation={observation} />
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">최근 {RECENT_HOURS}시간 날씨</h2>
        <RecentHistory observations={recent} />
      </section>
    </div>
  );
}
