"use client";

import { useEffect, useState } from "react";

import { type Station, getStations } from "@/lib/api";

export default function StationSelect({
  stationId,
  onChange,
}: {
  stationId: string;
  onChange: (id: string) => void;
}) {
  const [stations, setStations] = useState<Station[]>([]);

  useEffect(() => {
    getStations().then(setStations);
  }, []);

  const name = stations.find((s) => s.id === stationId)?.name ?? stationId;

  return (
    <select
      value={stationId}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
    >
      {stations.length === 0 && <option value={stationId}>{name}</option>}
      {stations.map((s) => (
        <option key={s.id} value={s.id}>
          {s.name}
        </option>
      ))}
    </select>
  );
}
