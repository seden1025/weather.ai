const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface Observation {
  station_id: string;
  observed_at: string;
  temperature: number | null;
  precipitation: number | null;
  wind_speed: number | null;
  humidity: number | null;
  pressure: number | null;
}

export interface AnomalyEvent {
  id: number;
  station_id: string;
  variable: string;
  observed_at: string;
  value: number;
  expected_low: number | null;
  expected_high: number | null;
  similar_past_event_ids: number[] | null;
  news_summary: string | null;
  news_sources: { title: string; link: string }[] | null;
  created_at: string;
}

export async function getCurrentWeather(stationId: string): Promise<Observation | null> {
  const res = await fetch(`${API_BASE_URL}/weather/current/${stationId}`, {
    cache: "no-store",
  });
  if (!res.ok) return null;
  return res.json();
}

export async function getRecentHistory(stationId: string, hours: number): Promise<Observation[]> {
  const url = new URL(`${API_BASE_URL}/weather/history/${stationId}`);
  url.searchParams.set("hours", String(hours));
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export async function getAnomalyEvents(stationId?: string): Promise<AnomalyEvent[]> {
  const url = new URL(`${API_BASE_URL}/anomaly/events`);
  if (stationId) url.searchParams.set("station_id", stationId);
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}
