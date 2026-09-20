import AnomalyPanel from "@/components/AnomalyPanel";
import RecentHistory from "@/components/RecentHistory";
import WeatherCard from "@/components/WeatherCard";
import { getAnomalyEvents, getCurrentWeather, getRecentHistory } from "@/lib/api";

const DEFAULT_STATION_ID = "108"; // 서울
const RECENT_HOURS = 5;

export default async function Home() {
  const [observation, recent, anomalies] = await Promise.all([
    getCurrentWeather(DEFAULT_STATION_ID),
    getRecentHistory(DEFAULT_STATION_ID, RECENT_HOURS),
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
        <h2 className="mb-3 text-lg font-semibold">최근 {RECENT_HOURS}시간 날씨</h2>
        <RecentHistory observations={recent} />
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">감지된 이상치</h2>
        <AnomalyPanel events={anomalies} />
      </section>
    </main>
  );
}
