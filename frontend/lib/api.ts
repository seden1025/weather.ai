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

export interface Station {
  id: string;
  name: string;
  lat: number;
  lon: number;
  distance_km?: number;
}

export async function getStations(): Promise<Station[]> {
  const res = await fetch(`${API_BASE_URL}/stations`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export async function getNearestStation(lat: number, lon: number): Promise<Station | null> {
  const url = new URL(`${API_BASE_URL}/stations/nearest`);
  url.searchParams.set("lat", String(lat));
  url.searchParams.set("lon", String(lon));
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) return null;
  return res.json();
}

export interface GeocodeResult {
  display_name: string;
  lat: number;
  lon: number;
}

export async function geocodeAddress(query: string): Promise<GeocodeResult[]> {
  const url = new URL(`${API_BASE_URL}/geocode/search`);
  url.searchParams.set("q", query);
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
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

export async function getOnDate(stationId: string, date: string): Promise<Observation[]> {
  const url = new URL(`${API_BASE_URL}/weather/on-date/${stationId}`);
  url.searchParams.set("date", date);
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export interface Forecast {
  horizon_hours: number;
  predicted_temperature: number;
  model_test_mae: number;
  based_on: string;
}

export async function getForecast(stationId: string): Promise<Forecast[]> {
  const res = await fetch(`${API_BASE_URL}/weather/forecast/${stationId}`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export interface Prediction {
  id: number;
  station_id: string;
  predict_date: string;
  sky_condition: string;
  wind_feel: string;
  memo: string | null;
  predicted_max_temp: number;
  predicted_sky_condition: string | null;
  ai_predicted_max_temp: number | null;
  ai_predicted_sky_condition: string | null;
  actual_max_temp: number | null;
  actual_rained: boolean | null;
  created_at: string;
}

export async function submitPrediction(
  stationId: string,
  body: {
    sky_condition: string;
    wind_feel: string;
    predicted_max_temp: number;
    predicted_sky_condition?: string;
    memo?: string;
  }
): Promise<Prediction | null> {
  const res = await fetch(`${API_BASE_URL}/predictions/${stationId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) return null;
  return res.json();
}

export async function getPredictions(stationId: string): Promise<Prediction[]> {
  const res = await fetch(`${API_BASE_URL}/predictions/${stationId}`, { cache: "no-store" });
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
