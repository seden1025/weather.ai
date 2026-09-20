import AnomalyPanel from "@/components/AnomalyPanel";
import WeatherCard from "@/components/WeatherCard";
import { getAnomalyEvents, getCurrentWeather } from "@/lib/api";

const DEFAULT_STATION_ID = "108"; // 서울

export default async function Home() {
  const [observation, anomalies] = await Promise.all([
    getCurrentWeather(DEFAULT_STATION_ID),
    getAnomalyEvents(DEFAULT_STATION_ID),
  ]);

  return (
    <main className="mx-auto max-w-3xl space-y-8 p-8">
      <h1 className="text-2xl font-bold">Weather AI</h1>

      <section>
        <h2 className="mb-3 text-lg font-semibold">현재 날씨</h2>
        <WeatherCard observation={observation} />
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">감지된 이상치</h2>
        <AnomalyPanel events={anomalies} />
      </section>
    </main>
  );
}
