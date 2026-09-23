import type { Observation } from "@/lib/api";
import { weatherIcon } from "@/lib/weatherIcon";

export default function WeatherCard({ observation }: { observation: Observation | null }) {
  if (!observation) {
    return (
      <div className="rounded-xl border border-gray-200 p-6 text-gray-500">
        관측 데이터가 없습니다.
      </div>
    );
  }

  const icon = weatherIcon(observation);

  return (
    <div className="rounded-xl border border-gray-200 p-6 shadow-sm">
      <h2 className="text-sm text-gray-500">{observation.station_id} 지점</h2>
      <div className="flex items-center gap-3">
        <span className="text-5xl" aria-hidden="true">
          {icon.emoji}
        </span>
        <div>
          <p className="text-4xl font-semibold">
            {observation.temperature != null ? `${observation.temperature}°C` : "-"}
          </p>
          <p className="text-sm text-gray-500">{icon.label}</p>
        </div>
      </div>
      <dl className="mt-4 grid grid-cols-2 gap-2 text-sm text-gray-600">
        <div>
          <dt>강수량</dt>
          <dd>{observation.precipitation ?? "-"} mm</dd>
        </div>
        <div>
          <dt>풍속</dt>
          <dd>{observation.wind_speed ?? "-"} m/s</dd>
        </div>
        <div>
          <dt>습도</dt>
          <dd>{observation.humidity ?? "-"} %</dd>
        </div>
        <div>
          <dt>기압</dt>
          <dd>{observation.pressure ?? "-"} hPa</dd>
        </div>
      </dl>
    </div>
  );
}
