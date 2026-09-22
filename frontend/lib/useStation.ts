"use client";

import { useEffect, useState } from "react";

const KEY = "weather-ai:selected-station";
const EVENT = "weather-ai:station-changed";

export function useSelectedStation(defaultId = "108") {
  const [stationId, setStationIdState] = useState(defaultId);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(KEY);
      if (saved) setStationIdState(saved);
    } catch {
      // localStorage 접근 불가(프라이빗 모드 등) - 기본값 유지
    }

    function onChange(e: Event) {
      const id = (e as CustomEvent<string>).detail;
      if (id) setStationIdState(id);
    }
    window.addEventListener(EVENT, onChange);
    return () => window.removeEventListener(EVENT, onChange);
  }, []);

  function setStationId(id: string) {
    setStationIdState(id);
    try {
      localStorage.setItem(KEY, id);
    } catch {
      // 무시
    }
    window.dispatchEvent(new CustomEvent(EVENT, { detail: id }));
  }

  return [stationId, setStationId] as const;
}
