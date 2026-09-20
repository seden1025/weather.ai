import type { Observation } from "@/lib/api";

export default function WeatherCard({ observation }: { observation: Observation | null }) {
  if (!observation) {
    return (
      <div className="rounded-xl border border-gray-200 p-6 text-gray-500">
        관측 데이터가 없습니다.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-gray-200 p-6 shadow-sm">
      <h2 className="text-sm text-gray-500">{observation.station_id} 지점</h2>
      <p className="text-4xl font-semibold">
        {observation.temperature != null ? `${observation.temperature}°C` : "-"}
      </p>
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
